from dotenv import load_dotenv
import os

load_dotenv()  # Charge les variables d’environnement si elles existent dans un fichier .env

class Config:
    # Sécurité
    SECRET_KEY = os.environ.get("SECRET_KEY", "une_clé_secrète")

    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CKEditor
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_FILE_UPLOADER = "main.upload"

    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'soukaina.ljaouhari@gmail.com'
    MAIL_PASSWORD = 'xcerusxwztjzdqfz'  
    MAIL_DEFAULT_SENDER = 'soukaina.ljaouhari@gmail.com'


    # Environnement
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"
