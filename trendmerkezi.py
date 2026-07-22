import random
import os
import feedparser
import tweepy
import logging

# Loglama yapılandırması
logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Twitter API anahtarları (v1 için)
consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
bearer_token = os.environ.get('BEARER_TOKEN')

# V1 ve V2 Twitter API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

# Hashtag dosyasını oku
def load_hashtags(file_path):
    try:
        with open(file_path, 'r') as file:
            hashtags = [line.strip() for line in file.readlines() if line.strip()]
        return hashtags
    except Exception as e:
        logging.error(f"Hashtag dosyası okunurken hata oluştu: {e}")
        return []

# Rastgele yorum seçimi
def select_random_comment(comments_file_path):
    try:
        with open(comments_file_path, 'r') as file:
            comments = file.readlines()
        return random.choice(comments).strip()
    except Exception as e:
        logging.error(f"Yorum dosyasından seçim yapılırken hata oluştu: {e}")
        return ""

# Rastgele resim seçimi
def select_random_image(images_path):
    try:
        images = [file for file in os.listdir(images_path) if file.endswith(('webp', 'png', 'jpg', 'jpeg'))]
        if not images:
            raise FileNotFoundError("Klasörde resim bulunamadı.")
        return os.path.join(images_path, random.choice(images))
    except Exception as e:
        logging.error(f"Resim seçimi sırasında hata oluştu: {e}")
        return ""

# Trendleri RSS feed'den çek
def get_trends(url):
    try:
        feed = feedparser.parse(url)
        trends = [entry.title for entry in feed.entries[:5]]
        return trends
    except Exception as e:
        logging.error(f"RSS feed'den veri çekme sırasında hata oluştu: {e}")
        return []

# Tweet gönderimi
def tweet(content, image_path, trends, comments_file_path, hashtags_file_path):
    try:
        media_id = api.media_upload(filename=image_path).media_id_string
        
        # Hashtag'leri dosyadan yükle
        hashtags_list = load_hashtags(hashtags_file_path)
        
        # Rastgele 3 hashtag seç
        selected_hashtags = random.sample(hashtags_list, 3)
        hashtags = " ".join(selected_hashtags)

        trends_string = "\n".join([f"{i+1}- {trend}" for i, trend in enumerate(trends)])
        comment = select_random_comment(comments_file_path)
        text = f"{comment}\nGüncel trendler şöyle:\n{trends_string}\n{hashtags}"
        
        client.create_tweet(text=text, media_ids=[media_id])
        logging.info("Tweet başarıyla gönderildi.")
    except Exception as e:
        logging.error(f'Tweet gönderme işlemi sırasında hata oluştu: {e}')

def main():
    # Google eski "trendingsearches/daily/rss" endpoint'ini kaldırdı (404).
    # Yeni "Trending Now" RSS'i geo=<ISO ülke kodu> ile çalışır.
    rss_url = "https://trends.google.com/trending/rss?geo=TR"
    images_path = "./images"
    comments_file_path = "./comments.txt"
    hashtags_file_path = "./hashtags.txt"
    
    trends = get_trends(rss_url)
    if not trends:
        logging.warning("Trend verisi çekilemedi, işlem iptal ediliyor.")
        return
    
    image_path = select_random_image(images_path)
    if not image_path:
        logging.warning("Resim bulunamadı, işlem iptal ediliyor.")
        return
    
    tweet(trends, image_path, trends, comments_file_path, hashtags_file_path)

if __name__ == "__main__":
    main()
