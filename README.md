# TrendMerkezi — X'te Güncel Trend Paylaşımı

TrendMerkezi, Türkiye'deki güncel arama trendlerini otomatik olarak toplayıp
**[@trendmerkezi](https://x.com/trendmerkezi)** hesabında; samimi bir yorum ve
bir görsel/video ile birlikte paylaşan bir Python botudur. Tamamen otomatiktir:
günde 4 kez, sosyal medyanın yoğun olduğu saatlerde kendiliğinden gönderi atar.

## Nasıl çalışır?

Her çalıştığında script şu adımları izler:

1. **Trendleri çeker** — Google'ın "Trending Now" verisinden (son 24 saat, `geo=TR`)
   [`trendspy`](https://pypi.org/project/trendspy/) ile taze/yükselen trendleri alır;
   biten, düşük hacimli veya aşırı uzun (haber-sorgusu) girdileri eler, yükseliş
   yüzdesi + hacme göre sıralayıp ilk **5**'i seçer.
2. **Yorum seçer** — `comments.txt` içinden rastgele, sıcak/esprili bir açılış cümlesi.
3. **Hashtag ekler** — `hashtags.txt` içinden rastgele en fazla 3 etiket.
4. **Görsel/video seçer** — `images/` klasöründen rastgele bir medya (`.webp`, `.png`,
   `.jpg`, `.jpeg`, `.mp4`).
5. **Metni güvenle kurar** — X'in ağırlıklı karakter sayımına göre 278 sınırını aşmamak
   için: **trendler her zaman korunur**; gerekirse önce hashtag sayısı 3→0 azaltılır,
   yetmezse daha kısa bir yorum seçilir.
6. **Paylaşır** — medyayı `tweepy` ile yükler (v1.1) ve tweet'i v2 API üzerinden atar;
   medya yüklenemezse gönderi düşmesin diye **yalnız-metin** olarak devam eder.
7. **Loglar** — önemli adımları ve hataları hem `app.log`'a hem de çalışma çıktısına yazar.

## Otomasyon (zamanlama)

Bot, GitHub Actions üzerinde (`.github/workflows/main.yml`, `workflow_dispatch`)
çalışır. GitHub'ın kendi `schedule`'ı gecikmeli tetiklediği için zamanlama **harici
bir Cloudflare Worker cron**'u ile yapılır. Günde **4 gönderi**:

| UTC | Türkiye (UTC+3) |
| --- | --- |
| 06:00 | 09:00 |
| 10:00 | 13:00 |
| 15:00 | 18:00 |
| 19:00 | 22:00 |

Cloudflare, workflow'u `dry_run: false` ile tetikler; manuel çalıştırmada varsayılan
`dry_run: true`'dur, yani yanlışlıkla tweet atılmaz.

## Kurulum

Gereksinimler `requirements.txt` içinde:

- [`trendspy`](https://pypi.org/project/trendspy/) — Google Trends "Trending Now" verisi
- [`tweepy`](https://pypi.org/project/tweepy/) — X/Twitter API istemcisi

### Adımlar

1. Repoyu klonlayın.
2. `pip install -r requirements.txt`
3. X API kimlik bilgilerinizi **ortam değişkeni** (veya GitHub Actions secret'ı) olarak verin:
   - `CONSUMER_KEY`
   - `CONSUMER_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`

   > Anahtarların nereden geldiği ve nasıl yenileneceği için aşağıdaki
   > **[Altyapı ve Kimlik Doğrulama](#altyapı-ve-kimlik-doğrulama-x-api)** bölümüne bakın.
4. İçerik dosyalarını hazırlayın: `images/` klasörüne görsel/video, `comments.txt` ve
   `hashtags.txt` dosyalarına her satıra bir öğe.
5. Çalıştırın: `python trendmerkezi.py`

### Yerel test (tweet atmadan)

`DRY_RUN=1 python trendmerkezi.py` — trendleri çeker, atılacak tweet'i **ekrana yazar**
ama **canlıya göndermez**. (`DRY_RUN` için kabul edilen değerler: `1`, `true`, `yes`.)

## Altyapı ve Kimlik Doğrulama (X API)

> Bu bölüm **özel/private** repo içindir; kurulumun nasıl çalıştığını belgeler.
> **Anahtar değerleri asla burada tutulmaz** — yalnızca yapı ve prosedür.

**Neden özel bir kurulum?** X, eski **developer.x.com Free tier**'ı kaldırdı
("no longer includes general access to API endpoints"). trendmerkezi'nin kendi
eski developer hesabı (proje: *trend*, app: *GTTrends* / `28275448`) bir Project'te
görünmesine rağmen v2 çağrılarında `client-not-enrolled` / 0 kota veriyor — yani ölü.
Token yenilemek veya app'i Project'ten çıkarıp eklemek bunu **çözmez**; sorun app
değil, hesabın **planıdır**.

**Çalışan kurulum:** Bot, **dovizmerkezi'nin `console.x.com` (Pay Per Use)** hesabı
(`account 1746913296043692032`) altında oluşturulmuş ayrı bir uygulama üzerinden çalışır:

- **App:** `TrendMerkezi` (app id `33229852`) — dovizmerkezi'nin kendi app'ine dokunulmadı.
- **İzin/Tip:** Read + Write, "Web App / Automated App or Bot".
- **Kime atıyor:** Tweet, **@trendmerkezi**'nin (`user id 751989891941142528`) OAuth
  1.0a kullanıcı token'ıyla atılır — yani gönderi @trendmerkezi'ye düşer.
- **Kota/masraf:** Kullanım **dovizmerkezi'nin Pay Per Use kredisinden** düşer
  (iki bot tek cüzdan; gözlenen maliyet düşük, tweet başına birkaç sent).

**Token'ı yenileme (3-bacaklı OAuth / PIN):** GitHub secret'larındaki `ACCESS_TOKEN` /
`ACCESS_TOKEN_SECRET` yalnızca @trendmerkezi'ye aittir; iptal edilmedikçe süresizdir.
Yeniden üretmek gerekirse (app'in Consumer Key/Secret'iyle):

```python
import tweepy
h = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, callback="oob")
print(h.get_authorization_url())          # linki @trendmerkezi olarak giriş yapıp aç
at, ats = h.get_access_token("PIN")       # ekranda çıkan PIN'i gir
# at / ats -> ACCESS_TOKEN / ACCESS_TOKEN_SECRET olarak GitHub secret'a yaz
```

> Yetkilendirme linkini açarken **mutlaka @trendmerkezi olarak giriş yapmış olun**
> (dovizmerkezi ile onaylarsanız token yanlış hesaba çıkar). Posting OAuth 1.0a
> kullanıcı bağlamıyla yapılır; `BEARER_TOKEN` create_tweet için gerekli değildir.

## Dosya yapısı

| Dosya | İşlev |
| --- | --- |
| `trendmerkezi.py` | Ana script |
| `comments.txt` | Rastgele seçilen açılış yorumları (her satır bir yorum) |
| `hashtags.txt` | Rastgele seçilen hashtag havuzu |
| `images/` | Paylaşılacak görsel/video havuzu |
| `requirements.txt` | Python bağımlılıkları |
| `.github/workflows/main.yml` | GitHub Actions iş akışı |
| `app.log` | Çalışma logları |

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## Yazar

[bucagdas](https://github.com/bucagdas)
