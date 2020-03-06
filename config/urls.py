"""
ioi URL Configuration
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from ioi.game.views import serve_angular

from ioi.profiles.views import (
    register_view,
    profile_view,
    teams_view,
    join_team,
    leaderboard_view,
)
from ioi.users import views as users_views

schema_view = get_schema_view(
    openapi.Info(title="IOI", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # angular
    path('', serve_angular, name='home'),

    # login, profile, social login
    path("login/", users_views.LoginView.as_view(), name="login"),
    path("social-auth/", include("social_django.urls", namespace="social")),
    re_path(
        r"^profile/(?P<nickname>[\w\-\.]+)/(?P<like>\w+)/$",
        profile_view,
        name="profile_view",
    ),
    re_path(r"^profile/(?P<nickname>[\w\-\.]+)/$", profile_view, name="profile_view"),
    path("profile/", profile_view, name="profile"),
    re_path(
        r"^leaderboard/(?P<race_type>[\d\-\.]+)/(?P<unit>[\w\-\.]+)/(?P<stat>[\w\-\.]+)/$",
        leaderboard_view,
        name="leaderboard_view",
    ),
    path("leaderboards/", leaderboard_view, name="leaderboard_view"),
    re_path(
        r"^(?P<affiliate_slug>[\w\-\.]+)/join/$",
        register_view,
        name="register_affiliate_view",
    ),
    # registration, login, logout, password reset and account activation
    url(r"^ioi/auth/", include("ioi.users.urls")),
    url(r"^ioi/auth/", include("ioi.users.urls_jwt")),
    # api
    url(r"^ioi/", include("ioi.game.urls_rest")), 
    # admin
    path("ioimin/", admin.site.urls),
    # swagger
    path(
        "openapi/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "swagger.json",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-json",
    ),
]
