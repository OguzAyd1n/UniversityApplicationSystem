# Üniversite Başvuru Sistemi

Bu proje, öğrencilerin üniversite başvurularını yönetebilecekleri, üniversiteler hakkında bilgi alabilecekleri ve diğer öğrencilerle iletişim kurabilecekleri bir web uygulamasıdır.

## Özellikler

- Kullanıcı kaydı ve girişi
- Facebook ile giriş
- Üniversite arama ve filtreleme
- Başvuru durumu takibi
- Kullanıcılar arası mesajlaşma
- İçerik paylaşımı
- Profil yönetimi
- İstatistik görüntüleme

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullaniciadi/universite-basvuru-sistemi.git
cd universite-basvuru-sistemi
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac için
venv\Scripts\activate  # Windows için
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
python
>>> from main import db
>>> db.create_all()
>>> exit()
```

5. Örnek verileri yükleyin:
```bash
python data_loader.py
```

6. Uygulamayı çalıştırın:
```bash
python main.py
```

## Ortam Değişkenleri

Uygulamayı çalıştırmadan önce aşağıdaki ortam değişkenlerini ayarlamanız gerekmektedir:

- `SECRET_KEY`: Flask uygulaması için gizli anahtar
- `EMAIL_USER`: E-posta gönderimi için kullanıcı adı
- `EMAIL_PASS`: E-posta gönderimi için şifre
- `RECAPTCHA_PUBLIC_KEY`: reCAPTCHA için public key
- `RECAPTCHA_PRIVATE_KEY`: reCAPTCHA için private key
- `SOCIAL_AUTH_FACEBOOK_KEY`: Facebook uygulaması için client ID
- `SOCIAL_AUTH_FACEBOOK_SECRET`: Facebook uygulaması için client secret

## Kullanım

1. Tarayıcınızda `http://localhost:5000` adresine gidin
2. Kayıt olun veya giriş yapın
3. Üniversiteleri görüntüleyin ve başvurun
4. Başvuru durumunuzu takip edin
5. Diğer kullanıcılarla iletişim kurun

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 