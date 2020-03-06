from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from ioi.game import models as game_models
from ioi.profiles import models as profile_models
from ioi.game import serializers
from ioi.helpers.race import get_time_remaining_to_the_next_race24
from ioi.helpers.race import get_time_remaining_to_current_race_to_finish
from ioi.helpers.race import estimate_time_until_race_start_seconds

from django.shortcuts import render

def serve_angular(request):
    return render(request, 'angular.html')


class RacesViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    API endpoint that allows races to be viewed or edited.
    """

    queryset = game_models.Race.objects.filter(
        players__gte=1, wins_paid=True, is_race24=False
    ).order_by("-pk")
    serializer_class = serializers.RaceSerializer

    def get_queryset(self):

        queryset = super().get_queryset()
        only_race24 = str(self.request.query_params.get("race24")).lower()

        if only_race24 in ["true", "1"]:

            queryset = game_models.Race.objects.filter(
                players__gte=1, wins_paid=True, is_race24=True
            ).order_by("-pk")
            serializer_class = serializers.RaceSerializer

        return queryset


class CarsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for cars showroom to be viewed.
    """

    queryset = game_models.CarShowroom.objects.all()
    serializer_class = serializers.CarShowroomSerializer


class ProfileViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for profiles to be viewed.
    """

    queryset = profile_models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type="object",
                    required=["id", "hash"],
                    properties={
                        "id": openapi.Schema(type="string"),
                        "hash": openapi.Schema(type="string"),
                        "email": openapi.Schema(type="string"),
                        "nickname": openapi.Schema(type="string"),
                        "affiliate_slug": openapi.Schema(type="string"),
                        "received_likes": openapi.Schema(type="integer"),
                        "is_admin": openapi.Schema(type="boolean"),
                        "is_investor": openapi.Schema(type="boolean"),
                    },
                ),
            )
        }
    )
    @action(detail=False)
    def me(self, request, *args, **kwargs):
        # assumes the user is authenticated, handle this according your needs
        my_profile = profile_models.Profile.objects.get(user=request.user)
        content = {
            "id": my_profile.user.id,
            "hash": my_profile.hash,
            "email": my_profile.user.email,
            "nickname": my_profile.user.nickname,
            "affiliate_slug": my_profile.affiliate_slug,
            "received_likes": my_profile.likes,
            "is_admin": my_profile.user.is_admin,
            "is_investor": my_profile.user.is_investor,
        }
        return Response(content)


class TeamsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for cars showroom to be viewed.
    """

    queryset = game_models.RacingTeam.objects.all()
    serializer_class = serializers.RacingTeamSerializer


class UpcomingRacesView(APIView):
    """
    API endpoint to display countdown to races.
    """

    def get(self, request, format=None):

        current_race = game_models.Race.objects.filter(
            is_race24=False, start__isnull=False
        ).order_by("-pk")[0]

        current_race24 = game_models.Race.objects.filter(
            is_race24=True, start__isnull=False
        ).order_by("-pk")[0]

        # Calculate time remaining to the next 24-hrs race
        current_race24_finishing_in_seconds, next_race24_starting_in_seconds = get_time_remaining_to_the_next_race24(
            current_race24
        )

        # Calculate time remainging to the next 3-mins race
        current_race_finishing_in_seconds, current_race_finishing_at, is_cancelled = get_time_remaining_to_current_race_to_finish(
            current_race
        )

        # XXX TODO put this onto model function......
        content = {
            "current_3mins_race": {
                "current_race_amount": current_race.race_amount,
                "current_race_finishing_in_seconds": current_race_finishing_in_seconds,
                "is_canceled": is_cancelled,
            },
            "current_24hrs_race": {
                "race_amount": current_race24.race_amount,
                "current_race24_finishing_in_seconds": current_race24_finishing_in_seconds,
                "next_race24_starting_in_seconds": next_race24_starting_in_seconds,
            },
            # Calculate time to individual 3-mins races start
            "next_$0_race_starts_in_seconds": estimate_time_until_race_start_seconds(
                0, current_race_finishing_in_seconds
            ),
            "next_$1_race_starts_in_seconds": estimate_time_until_race_start_seconds(
                1, current_race_finishing_in_seconds
            ),
            "next_$3_race_starts_in_seconds": estimate_time_until_race_start_seconds(
                3, current_race_finishing_in_seconds
            ),
            "next_$5_race_starts_in_seconds": estimate_time_until_race_start_seconds(
                5, current_race_finishing_in_seconds
            ),
            "next_$10_race_starts_in_seconds": estimate_time_until_race_start_seconds(
                10, current_race_finishing_in_seconds
            ),
        }
        return Response(content)


class AffiliateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint to list user affiliates.
    """

    serializer_class = serializers.AffiliatesSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type="array",
                    items=openapi.Schema(
                        type="object",
                        required=["id", "hash"],
                        properties={
                            "level": openapi.Schema(type="integer"),
                            "nickname": openapi.Schema(type="string"),
                            "email": openapi.Schema(type="email"),
                            "reward": openapi.Schema(type="integer"),
                        },
                    ),
                ),
            )
        }
    )
    def list(self, request):

        user = self.request.user
        queryset = profile_models.Affiliate.objects.filter(user=user)

        # XXX QUESTION IS THERE A BETTER WAY OF DOING THIS?

        decoupled_content = []

        for affiliate in queryset:
            a = {
                "level": 1,
                "nickname": affiliate.user.nickname,
                "email": affiliate.user.email,
                "reward": 0,
            }
            decoupled_content.append(a)

        return Response(decoupled_content)
