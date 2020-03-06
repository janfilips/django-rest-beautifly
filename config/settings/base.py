"""
Django settings for ioi project.
"""
import os
import environ
import datetime

from django.urls import reverse_lazy

##########################################################################################
# BASE SETTINGS
##########################################################################################

ROOT_DIR = environ.Path(__file__) - 3  # (ioi/config/settings/base.py - 3 = ioi/)
APPS_DIR = ROOT_DIR.path("ioi")
env = environ.Env()

##########################################################################################
# SECURITY WARNING: don't run with debug turned on in production!
##########################################################################################

DEBUG = env.bool("DJANGO_DEBUG", False)

##########################################################################################
# SECURITY WARNING: keep the secret key used in production secret!
##########################################################################################

SECRET_KEY = "v+b)!+mkkm(e9*znd3%=fmhu9qlk0$55pxewv*br#-r+6)ib#2"

##########################################################################################
# SECURITY INFO: allow hosts

ALLOWED_HOSTS = ["*"]

##########################################################################################
# Application definition
##########################################################################################

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "djoser",
    "drf_yasg",
    "social_django",
    "ioi.users.apps.UsersConfig",
    "ioi.game.apps.GameConfig",
    "ioi.profiles.apps.ProfilesConfig",
    "corsheaders",
    # "webpack_loader",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR.path("templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ]
        },
    }
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.google.GoogleOAuth2",
)

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "users.IoiUser"

##########################################################################################
# Users registration
##########################################################################################

REGISTRATION_OPEN = True
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window

##########################################################################################
# Social authentication
##########################################################################################

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

##########################################################################################
# Facebook
##########################################################################################

SOCIAL_AUTH_FACEBOOK_SCOPE = ["email", "user_link"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    "fields": "id, name, email, picture.type(large), link"
}
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [
    ("name", "name"),
    ("email", "email"),
    ("picture", "picture"),
    ("link", "profile_url"),
]

##########################################################################################
# Google
##########################################################################################

SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = [
    ("id", "user_id"),
    ("name", "name"),
    ("email", "user_email"),
    ("picture", "picture"),
    ("refresh_token", "refresh_token", True),
    ("expires_in", "expires"),
    ("token_type", "token_type", True),
]

##########################################################################################
# Login URLs
##########################################################################################

LOGIN_URL = reverse_lazy("login")
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = reverse_lazy("home")
LOGIN_ERROR_URL = "/login-error/"
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/xxx-new-users-redirect-url/'
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# For details on password validation see the
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

##########################################################################################
# Django REST
##########################################################################################

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

##########################################################################################
# JWT authentication
##########################################################################################

JWT_AUTH = {
    "JWT_EXPIRATION_DELTA": datetime.timedelta(minutes=5),
    "JWT_GET_USER_SECRET_KEY": "users.models.jwt_get_secret_key",
}

##########################################################################################
# Djoser settings
##########################################################################################

# See the docs for configuration options
# https://djoser.readthedocs.io/en/latest/settings.html

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
# Internationalization
##########################################################################################

# Localisation and internatlisation
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

##########################################################################################
# Static files (CSS, JavaScript, Images)
##########################################################################################

# For static files and it's Angular integration refer to the docs below
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = str(ROOT_DIR.path("..", "static"))
STATIC_URL = "/static/"

STATICFILES_DIRS = [str(APPS_DIR.path("static"))]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

##########################################################################################
# Swagger settings
##########################################################################################

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "api_key": {"type": "apiKey", "in": "header", "name": "Authorization"}
    }
}

##########################################################################################
