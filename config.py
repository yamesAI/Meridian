import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///meridian.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Astrology API (astrology-api.io Ultra+)
    ASTROLOGY_API_KEY = os.environ.get("ASTROLOGY_API_KEY", "")

    # Kimi / Moonshot AI
    KIMI_API_KEY = os.environ.get("KIMI_API_KEY", "")

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_PRO = os.environ.get("STRIPE_PRICE_PRO", "")       # $17/mo
    STRIPE_PRICE_PREMIUM = os.environ.get("STRIPE_PRICE_PREMIUM", "")  # $47/mo

    # Resend (transactional email)
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
    FROM_EMAIL = os.environ.get("FROM_EMAIL", "readings@themeridian.ai")
    FROM_NAME = os.environ.get("FROM_NAME", "The Meridian")

    # Mailchimp (broadcast list)
    MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY", "")
    MAILCHIMP_LIST_ID = os.environ.get("MAILCHIMP_LIST_ID", "")
    MAILCHIMP_SERVER_PREFIX = os.environ.get("MAILCHIMP_SERVER_PREFIX", "us1")

    # Meta Pixel
    META_PIXEL_ID = os.environ.get("META_PIXEL_ID", "")
    META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")  # Conversions API

    # TikTok Pixel
    TIKTOK_PIXEL_ID = os.environ.get("TIKTOK_PIXEL_ID", "")
    TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")  # Events API

    # App
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")
