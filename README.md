# TrendMerkezi: Twitter'da Güncel Trendleri Paylaş

TrendMerkezi, Twitter üzerinde güncel trendleri ve ilgi çekici içerikleri otomatik olarak paylaşan bir Python scriptidir. Bu script, belirlenen RSS beslemelerinden trend konuları çeker, rastgele yorumlar ve görseller seçerek bu trendleri özelleştirilmiş tweetlerle paylaşır. Kullanıcılar, bu script sayesinde Twitter'da dikkat çekici ve etkileşim yaratmayı amaçlayan içerikler oluşturabilirler.

## Özellikler

- **Güncel Trendler:** Google Trends üzerinden RSS feed aracılığıyla Türkiye'deki güncel trend konularını çeker.
- **Rastgele Yorum Seçimi:** Önceden belirlenen bir dosyadan rastgele yorumlar seçer.
- **Rastgele Görsel Seçimi:** Belirli bir klasördeki görseller arasından rastgele bir görsel seçer.
- **Otomatik Tweet Atma:** Seçilen yorum, trendler ve görsel ile özelleştirilmiş tweetler oluşturur ve bunları Twitter'da paylaşır.
- **Loglama:** Uygulamanın çalışma zamanındaki önemli adımları ve hataları bir log dosyasına kaydeder.

## Kurulum

TrendMerkezi'nin çalışması için Python'un yüklü olması ve aşağıdaki Python kütüphanelerinin kurulmuş olması gerekmektedir:

- `feedparser`: RSS feedlerini işlemek için kullanılır.
- `tweepy`: Twitter API ile etkileşim kurmak için kullanılır.
- `os`, `random`, `logging`: Scriptin temel işlevselliği için gerekli standart Python modülleri.

### Adımlar

1. Bu repoyu klonlayın veya indirin.
2. Gerekli kütüphaneleri yüklemek için `pip install -r requirements.txt` komutunu çalıştırın.
3. Twitter API anahtarlarınızı edinin ve aşağıdaki ortam değişkenleri olarak sisteminize ekleyin:
   - `CONSUMER_KEY`
   - `CONSUMER_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`
4. `images` klasörünü ve `comments.txt` dosyasını hazırlayın. Görseller `images` klasöründe, yorumlar ise her satırda bir yorum olacak şekilde `comments.txt` dosyasında bulunmalıdır.
5. Scripti çalıştırmak için terminal veya komut satırından `python trendmerkezi.py` komutunu kullanın.

## Kullanım

Script, her çalıştırıldığında aşağıdaki adımları otomatik olarak gerçekleştirir:

1. Güncel trendleri Google Trends RSS feed'inden çeker.
2. `images` klasöründen rastgele bir görsel seçer.
3. `comments.txt` dosyasından rastgele bir yorum seçer.
4. Seçilen görsel, yorum ve trend bilgilerini içeren bir tweet oluşturur ve Twitter'da paylaşır.

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---
