from .base import *  # noqa
import os

##########################################################################################
# DEVELOP SETTINGS
##########################################################################################

ROOT_DIR = environ.Path(__file__) - 3  # (ioi/config/settings/develop.py - 3 = ioi/)
APPS_DIR = ROOT_DIR.path("ioi")
env = environ.Env()

##########################################################################################
# SECURITY WARNING: debug should always be false unless you are a developer
##########################################################################################

DEBUG = True

##########################################################################################
# Game settings
##########################################################################################

RACES_DURATION_SECONDS = 25
DELAY_BETWEEN_RACES = 2
RACES_ORDER = [0, 1, 3, 5, 10]

##########################################################################################
# Social Keys
##########################################################################################

SOCIAL_AUTH_FACEBOOK_KEY = "711495712675280"  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = "87ed0367399cc9a8f803b95d771b3414"  # App Secret
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
    "555380142152-t9t6kl6ril61ac8dg5kpdiu3j32smv5l.apps.googleusercontent.com"
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "bTofj8EIizugdHps4fuhSylp"  # Google+ App Secret

##########################################################################################
# Binance API
##########################################################################################

BINANCE_KEY = "QgfdxURuwcm2yvuJKmBC83nEMlCAya4wDoN5qVvnICnxJMOIknk5XMYWu1bRKBYC"
BINANCE_SECRET = "tRKJgeOHnirxyKfmhPAojdokVy9HRVepaAPYb8S1ubtYN373aU92kP8sLZecDY9G"

##########################################################################################
# Email settings
##########################################################################################

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

##########################################################################################
# Djoser
##########################################################################################

DJOSER = {
    "DOMAIN": "beta.ioi-game.com",
    "SITE_NAME": "ioi-game.com",
    "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "user/activation/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": False,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": False,
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
# Database settings
##########################################################################################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ioi_devel",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

##########################################################################################
