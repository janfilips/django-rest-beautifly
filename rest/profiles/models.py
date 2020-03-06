import logging

from uuid import uuid4

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE
    )
    hash = models.UUIDField(
        default=uuid4, editable=False, help_text="This is used for internal reference."
    )
    affiliate_slug = models.SlugField(max_length=200, unique=True)
    referral = models.CharField(max_length=200, blank=True)
    credit = models.DecimalField(default=0, max_digits=20, decimal_places=6)

    total_bet_amount = models.DecimalField(default=0, max_digits=10, decimal_places=6)
    total_win_points = models.PositiveIntegerField(default=0)
    total_win_amount = models.DecimalField(default=0, max_digits=10, decimal_places=6)

    is_robot = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    likes = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "profiles_profiles"

    def affiliate_with_slug(self, slug: str) -> bool:
        """Affiliate user to another user based on affiliate_slug of another user."""
        try:
            other_profile = Profile.objects.get(affiliate_slug=slug)
        except Profile.DoesNotExist:
            logger.warning("Unknown slug %s for affiliation.", slug)
            return False
        else:
            Affiliate.objects.create(user=other_profile.user, affiliate=self.user)
            return True


class Like(models.Model):

    liked = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="likes"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "profiles_likes"


class Affiliate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="affiliates",
        help_text="The owner of the affiliate link.",
    )
    affiliate = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="affiliate_with",
        help_text="The user who uses affiliate link.",
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "profiles_affiliate"

    def __str__(self):
        return f"{self.user} <- {self.affiliate}"
