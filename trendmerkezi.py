import os
import sys
import time
import random
import logging
import unicodedata

import tweepy
from trendspy import Trends

# X/Twitter karakter limiti (Premium değilse 280). Güvenlik payı için biraz düşük.
TWEET_LIMIT = 278

# Loglama: hem app.log'a hem stdout'a (GitHub Actions loglarında görünsün)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a', encoding='utf-8'),
        logging.StreamHandler(),
    ],
    force=True,
)

# Twitter API anahtarları (ortam değişkenleri)
consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
bearer_token = os.environ.get('BEARER_TOKEN')

# DRY_RUN=1 iken tweet ATILMAZ; sadece ne atılacağı ekrana yazılır (yerel test için)
DRY_RUN = os.environ.get('DRY_RUN', '').strip().lower() in ('1', 'true', 'yes')


def get_twitter_clients():
    """Tweepy v1 (medya) + v2 (tweet) istemcileri — yalnızca gerçek gönderimde."""
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    client = tweepy.Client(
        bearer_token, consumer_key, consumer_secret,
        access_token, access_token_secret, wait_on_rate_limit=True,
    )
    return api, client


def load_hashtags(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Hashtag dosyası okunurken hata: {e}")
        return []


def select_random_comment(comments_file_path):
    try:
        with open(comments_file_path, 'r', encoding='utf-8') as f:
            comments = [line.strip() for line in f if line.strip()]
        return random.choice(comments) if comments else ""
    except Exception as e:
        logging.error(f"Yorum seçilirken hata: {e}")
        return ""


def select_random_image(images_path):
    try:
        media = [f for f in os.listdir(images_path)
                 if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg', '.mp4'))]
        if not media:
            raise FileNotFoundError("Klasörde medya bulunamadı.")
        return os.path.join(images_path, random.choice(media))
    except Exception as e:
        logging.error(f"Medya seçimi sırasında hata: {e}")
        return ""


def get_trends(geo='TR', hours=24, count=5):
    """Google 'Trending Now' (son {hours} saat) verisinden taze/yükselen ilk
    {count} trendi seçer. Eski RSS/pytrends kaldırıldı; trendspy kullanılıyor."""
    try:
        items = Trends().trending_now(geo=geo, hours=hours)

        def started(it):
            ts = getattr(it, 'started_timestamp', None)
            if isinstance(ts, list):
                ts = ts[0] if ts else 0
            return ts or 0

        # Aktif, anlamlı hacimli ve aşırı uzun olmayan (haber-sorgusu değil) trendler
        cand = [it for it in items
                if not getattr(it, 'is_trend_finished', False)
                and (getattr(it, 'volume', 0) or 0) >= 5000
                and len(it.keyword) <= 45]

        # Sıralama: yükseliş % -> hacim -> tazelik (daha yeni başlayan önce)
        cand.sort(
            key=lambda it: (
                getattr(it, 'volume_growth_pct', 0) or 0,
                getattr(it, 'volume', 0) or 0,
                started(it),
            ),
            reverse=True,
        )
        trends = [it.keyword for it in cand[:count]]

        if not trends:  # emniyet: filtre boş kaldıysa en yüksek hacimliler
            items.sort(key=lambda it: (getattr(it, 'volume', 0) or 0), reverse=True)
            trends = [it.keyword for it in items[:count]]

        logging.info(f"{len(trends)} trend seçildi: {trends}")
        return trends
    except Exception as e:
        logging.error(f"Trend verisi çekilirken hata: {e}")
        return []


def weighted_len(s):
    """X'in ağırlıklı karakter sayımına yaklaşım: emoji/semboller 2, diğerleri 1."""
    total = 0
    for ch in s:
        if ord(ch) >= 0x1F000 or unicodedata.category(ch) in ('So', 'Sk'):
            total += 2
        else:
            total += 1
    return total


def build_tweet_text(trends, comments_file_path, hashtags_file_path, limit=TWEET_LIMIT):
    """Tweet metnini kurar. TRENDLER HER ZAMAN KORUNUR; limit aşılırsa önce
    hashtag sayısı azaltılır (3->0), yetmezse daha kısa bir yorum seçilir."""
    trends_block = "\n".join(f"{i + 1}- {t}" for i, t in enumerate(trends))

    comments = load_hashtags(comments_file_path)   # satırları yükler
    hashtags_list = load_hashtags(hashtags_file_path)
    tags3 = random.sample(hashtags_list, min(3, len(hashtags_list))) if hashtags_list else []
    comment = random.choice(comments) if comments else ""

    def compose(cmt, ntags):
        parts = ([cmt] if cmt else []) + [trends_block]
        if ntags:
            parts.append(" ".join(tags3[:ntags]))
        return "\n".join(parts)

    # 1) Seçilen yorumla, hashtag'i 3'ten 0'a azaltarak dene
    for ntags in (3, 2, 1, 0):
        text = compose(comment, ntags)
        if weighted_len(text) <= limit:
            return text
    # 2) Hâlâ uzunsa: hashtag'siz, en kısa yorumdan başlayarak dene
    for cmt in sorted(comments, key=weighted_len):
        text = compose(cmt, 0)
        if weighted_len(text) <= limit:
            return text
    # 3) Son çare: sadece trendler
    return trends_block


def _twitter_error(e):
    """Tweepy hatasından tanılama için ayrıntı çıkarır (kod, mesaj, gövde)."""
    parts = [str(e)]
    for attr in ('api_codes', 'api_messages'):
        v = getattr(e, attr, None)
        if v:
            parts.append(f"{attr}={v}")
    resp = getattr(e, 'response', None)
    if resp is not None:
        try:
            parts.append(f"body={resp.text[:300]}")
        except Exception:
            pass
    return " | ".join(parts)


def tweet(text, image_path):
    if DRY_RUN:
        print("=== DRY_RUN: gönderilecek tweet (canlıya ATILMADI) ===")
        print(text)
        print(f"[medya: {image_path}]")
        logging.info("DRY_RUN aktif — tweet atılmadı.")
        return
    try:
        api, client = get_twitter_clients()
    except Exception as e:
        logging.error(f"Twitter istemcisi kurulamadı: {e}")
        return

    # Medya (v1.1 media_upload) — başarısız olursa (ör. API katmanı v1.1'i
    # desteklemiyorsa) metin-olarak devam et, böylece gönderi büsbütün düşmesin.
    media_ids = None
    if image_path:
        try:
            media_ids = [api.media_upload(filename=image_path).media_id_string]
        except Exception as e:
            logging.error(f"Medya yüklenemedi (v1.1 media_upload): {_twitter_error(e)}")

    try:
        client.create_tweet(text=text, media_ids=media_ids)
        logging.info(f"Tweet gönderildi. Medya: {image_path if media_ids else 'YOK (yalnız metin)'}")
    except Exception as e:
        logging.error(f"Tweet gönderilemedi (v2 create_tweet): {_twitter_error(e)}")
        # TANI: okuma (get_me) çalışıyor mu? Yazma mı yoksa kimlik/anahtar mı sorunlu, ayırt et.
        try:
            me = client.get_me()
            u = getattr(me, 'data', None)
            logging.error(f"TANI: get_me BAŞARILI -> auth geçerli, sorun YAZMA izni/kotası. Hesap: @{getattr(u, 'username', '?')}")
        except Exception as e2:
            logging.error(f"TANI: get_me de BAŞARISIZ -> kimlik/anahtar çifti hatalı (kopyalama/uyuşmazlık): {_twitter_error(e2)}")


def main():
    trends = get_trends(geo='TR', hours=24, count=5)
    if not trends:
        logging.warning("Trend verisi çekilemedi, işlem iptal ediliyor.")
        return

    image_path = select_random_image("./images")
    if not image_path and not DRY_RUN:
        logging.warning("Medya bulunamadı, işlem iptal ediliyor.")
        return

    text = build_tweet_text(trends, "./comments.txt", "./hashtags.txt")
    tweet(text, image_path)


if __name__ == "__main__":
    main()
