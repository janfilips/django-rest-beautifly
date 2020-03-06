from ioi.game.models import Race, CarShowroom, RacingTeam
from ioi.profiles.models import Affiliate, Profile
from rest_framework import serializers


class AffiliatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Affiliate
        fields = ["user", "affiliate"]


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ["hash", "affiliate_slug", "likes"]


class RaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Race
        fields = [
            "id",
            "is_race24",
            "players",
            "race_hash",
            "start",
            "start_coins_price",
            "race_duration_seconds",
            "finish",
            "finish_coins_price",
            "coins_performance",
            "cars_performance_at_finish",
            "err_prolonged_game",
            "err_prolonged_game_time_delta",
            "race_amount",
            "wins_paid",
        ]


class CarShowroomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CarShowroom
        fields = ["car_model", "car_boost", "car_extras", "car_price"]


class RacingTeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RacingTeam
        fields = ["name", "base_coins_portfolio", "cost_to_join_in"]
