# config.py

import os

class Config:
    # Flask ve veritabanı yapılandırması
    SECRET_KEY = 'your-secret-key-here'  # Güvenlik için rastgele bir string kullanın
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # E-posta yapılandırması
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    # Dosya yükleme yapılandırması
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    UPLOAD_FOLDER = 'static/profile_pics'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

SOCIAL_AUTH_FACEBOOK_KEY = 'your-facebook-key'
SOCIAL_AUTH_FACEBOOK_SECRET = 'your-facebook-secret'
