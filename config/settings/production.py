from .base import *  # noqa
import os
import environ

##########################################################################################
# PRODUCTION SETTINGS (!)
##########################################################################################

ROOT_DIR = environ.Path(__file__) - 3  # (ioi/config/settings/production.py - 3 = ioi/)
APPS_DIR = ROOT_DIR.path("ioi")
env = environ.Env()

##########################################################################################
# SECURITY WARNING: don't run with debug turned on in production!
##########################################################################################

DEBUG = False

##########################################################################################
# SECURITY WARNING: keep the secret key used in production secret!
##########################################################################################

SECRET_KEY = env.string("DJANGO_DEBUG", False)

##########################################################################################
# Game settings
##########################################################################################

RACES_DURATION_SECONDS = 180
DELAY_BETWEEN_RACES = 120
RACES_ORDER = [0, 10, 0, 1, 0, 3, 0, 5, 0, 1, 0, 3, 0, 5, 0, 1, 0, 3, 0, 5, 0, 1, 0, 3]

##########################################################################################
# Social Keys
##########################################################################################

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv("SOCIAL_AUTH_FACEBOOK_KEY")  # Facebook App ID
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv(
    "SOCIAL_AUTH_FACEBOOK_SECRET"
)  # Facebook App Secret

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"
)  # Google+ App Key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"
)  # Google+ App Secret

##########################################################################################
# Binance API
##########################################################################################

BINANCE_KEY = os.getenv("BINANCE_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")

##########################################################################################
# Database settings
##########################################################################################

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "admin@ioi-game.com"
EMAIL_HOST_PASSWORD = ""  # XXX get from env
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "info@ioi-game.com"

##########################################################################################
# Email settings
##########################################################################################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ioi_beta",  # XXX TODO parametrise this.....
        "USER": "postgres",
        "PASSWORD": "",  # XXX TODO this should go on the parameter....
        "HOST": "ioi-devel.ca8gq0tql2v8.eu-central-1.rds.amazonaws.com",
        "PORT": "5432",
    }
}

##########################################################################################
