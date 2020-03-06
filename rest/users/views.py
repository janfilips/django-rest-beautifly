import logging

from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from djoser import views as djoser_views
from djoser.conf import settings as djoser_settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt import views as jwt_views

from . import forms, serializers

logger = logging.getLogger(__name__)


class LoginView(auth_views.LoginView):
    form_class = forms.LoginForm
    template_name = "login.html"


# Copies of the jwt classes just for purpose of adding documentation
# ------------------------------------------------------------------
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type="object",
                    required=["refresh", "access"],
                    properties={
                        "refresh": openapi.Schema(type="string"),
                        "access": openapi.Schema(type="string"),
                    },
                ),
            )
        }
    ),
)
class TokenObtainPairView(jwt_views.TokenObtainPairView):
    pass


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type="object",
                    required=["access"],
                    properties={"access": openapi.Schema(type="string")},
                ),
            )
        }
    ),
)
class TokenRefreshView(jwt_views.TokenRefreshView):
    pass


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="", schema=openapi.Schema(type="object")
            )
        }
    ),
)
class TokenVerifyView(jwt_views.TokenVerifyView):
    pass


# Basic Djoser viewset for user with added action endpoint for affiliate users.
class UserViewSet(djoser_views.UserViewSet):
    def get_serializer_class(self):
        if self.action == "affiliate_with":
            return serializers.AffiliateSlugSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "affiliate_with":
            self.permission_classes = djoser_settings.PERMISSIONS.user_create
        return super().get_permissions()

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: "Success",
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Affiliate slug not found.",
                schema=openapi.Schema(
                    type="object",
                    properties={
                        "affiliate_slug": openapi.Schema(
                            type="array", items=openapi.Schema(type="string")
                        )
                    },
                ),
            ),
            status.HTTP_403_FORBIDDEN: "User is already affiliated.",
        }
    )
    @action(["post"], detail=True)
    def affiliate_with(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if hasattr(user, "affiliate_with"):
            logger.warning("User %s is already affiliated", user)
            return Response(
                "User is already affiliated.", status=status.HTTP_403_FORBIDDEN
            )

        affiliate_slug = serializer.validated_data["affiliate_slug"]
        if user.profile.affiliate_with_slug(affiliate_slug):
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
