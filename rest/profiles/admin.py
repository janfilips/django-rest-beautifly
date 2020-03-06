from django.contrib import admin

from . import models


class AffiliateInline(admin.TabularInline):
    model = models.Affiliate


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "credit", "affiliate_slug", "is_robot"]
    list_filter = ["is_robot"]


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "liked", "created"]


@admin.register(models.Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ["user", "affiliate", "created"]
