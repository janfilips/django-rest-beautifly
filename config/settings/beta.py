from .base import *  # noqa
import os

##########################################################################################
# DEVELOP SETTINGS
##########################################################################################

ROOT_DIR = environ.Path(__file__) - 3  # (ioi/config/settings/beta.py - 3 = ioi/)
APPS_DIR = ROOT_DIR.path("ioi")
env = environ.Env()

##########################################################################################
# SECURITY WARNING: don't run with debug turned on in production!
##########################################################################################

DEBUG = env.bool("DJANGO_DEBUG", False)

##########################################################################################
# SECURITY WARNING: keep the secret key used in production secret!
##########################################################################################

SECRET_KEY = "v+b)!+mkkJanko-m(e9*znd3%=fmhu9qlk0$55pxewv*br#-r+6)ib#2"

##########################################################################################
# Game settings
##########################################################################################

RACES_DURATION_SECONDS = 30
DELAY_BETWEEN_RACES = 10
RACES_ORDER = [0, 1, 3, 5, 10]

##########################################################################################
# Social Keys
##########################################################################################

SOCIAL_AUTH_FACEBOOK_KEY = ""  # XXX get from env
SOCIAL_AUTH_FACEBOOK_SECRET = ""  # XXX get from env
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ""  # XXX get from env
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ""  # XXX get from env

##########################################################################################
# Binance API
##########################################################################################

BINANCE_KEY = ""  # XXX get from env
BINANCE_SECRET = ""  # XXX get from env

##########################################################################################
# Database settings
##########################################################################################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ioi_beta",
        "USER": "postgres",
        "PASSWORD": "",  # XXX get from env
        "HOST": "ioi-devel.ca8gq0tql2v8.eu-central-1.rds.amazonaws.com",
        "PORT": "5432",
    }
}

##########################################################################################
# Email
##########################################################################################

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "admin@ioi-game.com"
EMAIL_HOST_PASSWORD = ""  # XXX get from env
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "info@ioi-game.com"

##########################################################################################
# Djoser
##########################################################################################

DJOSER = {
    "DOMAIN": "beta.ioi-game.com",
    "SITE_NAME": "ioi-game.com",
    "ACTIVATION_URL": "user/activation/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "SERIALIZERS": {
        "activation": "djoser.serializers.ActivationSerializer",
        "password_reset": "djoser.serializers.SendEmailResetSerializer",
        "user_create": "ioi.users.serializers.UserRegistrationSerializer",
        "user_create_password_retype": "djoser.serializers.UserCreatePasswordRetypeSerializer",
        "user": "djoser.serializers.UserSerializer",
        "current_user": "djoser.serializers.UserSerializer",
        "token": "djoser.serializers.TokenSerializer",
        "token_create": "djoser.serializers.TokenCreateSerializer",
    },
}

##########################################################################################
