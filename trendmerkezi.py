import os
import random
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

def get_trends(url):
    try:
        logging.info('RSS feedden veri çekiliyor...')
        feed = feedparser.parse(url)
        if feed.bozo == 1:
            logging.error(f'RSS feedden veri alınamadı: {feed.bozo_exception}')
            return []
        trends = [entry.title for entry in feed.entries[:5]]
        logging.info('Veri çekme işlemi tamamlandı.')
        return trends
    except Exception as e:
        logging.error(f'RSS feedden veri çekilirken hata oluştu: {e}')
        return []

def select_random_image(images_path):
    try:
        logging.info('Rastgele resim seçiliyor...')
        images = [file for file in os.listdir(images_path) if file.endswith(('webp', 'png', 'jpg', 'jpeg'))]
        if not images:
            raise FileNotFoundError('Klasörde resim bulunamadı.')
        selected_image = os.path.join(images_path, random.choice(images))
        logging.info('Resim seçme işlemi tamamlandı.')
        return selected_image
    except Exception as e:
        logging.error(f'Resim seçme işlemi sırasında hata oluştu: {e}')
        return None

def select_random_comment(comments_file_path):
    try:
        logging.info('Rastgele yorum seçiliyor...')
        with open(comments_file_path, 'r') as file:
            comments = file.readlines()
        if not comments:
            raise ValueError('Yorum dosyası boş.')
        selected_comment = random.choice(comments).strip()
        logging.info('Yorum seçme işlemi tamamlandı.')
        return selected_comment
    except Exception as e:
        logging.error(f'Yorum seçme işlemi sırasında hata oluştu: {e}')
        return None

def tweet(content, image_path, trends, comments_file_path):
    try:
        if image_path is None:
            raise ValueError('Tweet için geçerli bir resim bulunamadı.')
        media_id = api.media_upload(filename=image_path).media_id_string
        trends_string = "\n".join([f"{i+1}- {trend}" for i, trend in enumerate(trends)])
        hashtags = "#gündem 📰 #trend 🔥 #trendmerkezi 📊"
        comment = select_random_comment(comments_file_path)
        if comment is None:
            raise ValueError('Tweet için geçerli bir yorum bulunamadı.')
        text = f"{comment}\nGüncel trendler şöyle:\n{trends_string}\n{hashtags}"
        client.create_tweet(text=content, media_ids=[media_id])
        logging.info("Tweet başarıyla gönderildi.")
    except Exception as e:
        logging.error(f'Tweet gönderme işlemi sırasında hata oluştu: {e}')

def main():
    try:
        rss_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=TR"
        images_path = "./images"
        comments_file_path = "./comments.txt"
        
        trends = get_trends(rss_url)
        if not trends:
            logging.warning('Trend verisi alınamadı, tweet atılmayacak.')
            return
        
        image_path = select_random_image(images_path)
        if image_path is None:
            logging.warning('Geçerli bir resim bulunamadı, tweet atılmayacak.')
            return
        
        comment = select_random_comment(comments_file_path)
        if comment is None:
            logging.warning('Geçerli bir yorum bulunamadı, tweet atılmayacak.')
            return
        
        trends_string = "\n".join([f"{i+1}- {trend}" for i, trend in enumerate(trends)])
        hashtags = "#gündem 📰 #trend 🔥 #trendmerkezi 📊"
        content = f"{comment}\nGüncel trendler şöyle:\n{trends_string}\n{hashtags}"
        
        tweet(content, image_path, trends, comments_file_path)
    except Exception as e:
        logging.error(f'Genel hata oluştu: {e}')

if __name__ == "__main__":
    main()
