from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from rest_framework import serializers


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ("id", "email", "nickname", "password")


def affiliate_slug_exists(value):
    if (
        not get_user_model()
        .objects.filter(profile__affiliate_slug__iexact=value)
        .exists()
    ):
        raise serializers.ValidationError("Affiliate not found.")


class AffiliateSlugSerializer(serializers.Serializer):
    affiliate_slug = serializers.CharField(
        max_length=200, validators=[affiliate_slug_exists]
    )
