from django.contrib import admin

from . import models


@admin.register(models.CarShowroom)
class CarShowroomAdmin(admin.ModelAdmin):
    list_display = ["car_model", "car_boost", "car_price"]


@admin.register(models.RacingTeam)
class RacingTeamAdmin(admin.ModelAdmin):
    list_display = ["name", "cost_to_join_in"]
