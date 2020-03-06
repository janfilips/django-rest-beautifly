from django.urls import include, path
from rest_framework import routers
from ioi.game import views

router = routers.DefaultRouter()
router.register(r"cars/showroom", views.CarsViewSet)
router.register(r"teams", views.TeamsViewSet)
router.register(r"affiliates", views.AffiliateViewSet, basename="affiates")
router.register(r"races", views.RacesViewSet, basename="races")
router.register(r"drivers", views.ProfileViewSet, basename="drivers")

# Wire up our API using automatic URL routing.
urlpatterns = [
    path("races/upcoming/", views.UpcomingRacesView.as_view()),
    path("", include(router.urls)),
]
