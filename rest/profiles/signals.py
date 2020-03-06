import random

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="create_profile")
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        affiliate_slug = instance.nickname + str(random.randint(12021, 8200121))

        models.Profile.objects.get_or_create(
            user=instance, defaults={"affiliate_slug": affiliate_slug}
        )
