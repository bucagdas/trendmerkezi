import os
import random
import feedparser
import tweepy
import logging

# Loglama yapılandırması
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    logging.info('RSS feedden veri çekiliyor...')
    feed = feedparser.parse(url)
    trends = [entry.title for entry in feed.entries[:5]]
    logging.info('Veri çekme işlemi tamamlandı.')
    return trends

def select_random_image(images_path):
    logging.info('Rastgele resim seçiliyor...')
    images = [file for file in os.listdir(images_path) if file.endswith(('webp', 'png', 'jpg', 'jpeg'))]
    selected_image = os.path.join(images_path, random.choice(images))
    logging.info('Resim seçme işlemi tamamlandı.')
    return selected_image

def select_random_comment(comments_file_path):
    logging.info('Rastgele yorum seçiliyor...')
    with open(comments_file_path, 'r') as file:
        comments = file.readlines()
    selected_comment = random.choice(comments).strip()
    logging.info('Yorum seçme işlemi tamamlandı.')
    return selected_comment

def tweet(content, image_path, trends, comments_file_path):
    media_id = api.media_upload(filename=image_path).media_id_string
    trends_string = "\n".join([f"{i+1}- {trend}" for i, trend in enumerate(trends)])
    hashtags = "#gündem 📰 #trend 🔥 #trendmerkezi 📊"
    comment = select_random_comment(comments_file_path)
    text = f"{comment}\nGüncel trendler şöyle:\n{trends_string}\n{hashtags}"
    client.create_tweet(text=content, media_ids=[media_id])
    logging.info("Tweet başarıyla gönderildi.")

def main():
    rss_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=TR"
    images_path = "./images"
    comments_file_path = "./comments.txt"
    
    trends = get_trends(rss_url)
    image_path = select_random_image(images_path)
    comment = select_random_comment(comments_file_path)
    trends_string = "\n".join([f"{i+1}- {trend}" for i, trend in enumerate(trends)])
    hashtags = "#gündem 📰 #trend 🔥 #trendmerkezi 📊"
    content = f"{comment}\nGüncel trendler şöyle:\n{trends_string}\n{hashtags}"
    
    tweet(content, image_path, trends, comments_file_path)

if __name__ == "__main__":
    main()
