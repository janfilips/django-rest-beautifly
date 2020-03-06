from django.utils import timezone
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField

# ONE_DAY_IN_SECONDS = 86400
ONE_DAY_IN_SECONDS = 7200


class Ticker(models.Model):

    prices = JSONField(default=dict)
    epoch_prices = JSONField(default=dict)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "game_tickers"


class CarShowroom(models.Model):

    car_model = models.PositiveSmallIntegerField(default=0)
    car_boost = models.FloatField(default=0)
    car_extras = JSONField(default=dict)
    car_price = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        db_table = "game_car_showrooms"


class RacingTeam(models.Model):

    name = models.CharField(max_length=20)
    base_coins_portfolio = JSONField(default=dict)
    cost_to_join_in = models.DecimalField(default=5, max_digits=10, decimal_places=6)

    class Meta:
        db_table = "game_racing_teams"


class TeamMemberManager(models.Manager):
    def get_user_team(self, user) -> "TeamMember":
        """Returns membership of the first team which the user is member of."""
        queryset = super().get_queryset()
        return queryset.filter(user=user).first()


class TeamMember(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    team = models.ForeignKey(RacingTeam, on_delete=models.PROTECT, related_name="likes")
    joined = models.DateTimeField(auto_now_add=True)

    objects = TeamMemberManager()

    class Meta:
        db_table = "game_team_members"


class Car(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    car = models.ForeignKey(CarShowroom, on_delete=models.PROTECT)
    car_wins_count = models.PositiveIntegerField(default=0)
    car_wins_roi_avg = models.FloatField(default=0)
    car_wins_total_points = models.PositiveIntegerField(default=0)
    car_wins_total_amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=6
    )
    bought = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "game_cars"

    def get_user_cars_fleet(self, user):

        cars = Car.objects.filter(user=user)

        return cars

    def get_new_cars_for_sale(self):

        new_cars = CarShowroom.objects.all()

        return new_cars

    def get_user_availabe_cars(self, user, race):

        exclude_cars = []
        user_availabl_cars = []

        if race.is_24race:
            bets = Bet.objects.filter(user=user, race=race, is_race24=True)
        else:
            bets = Bet.objects.filter(user=user, race=race, is_race24=False)

        for b in bets:
            exclude_cars.append(b.car)

        user_cars = Car.objects.filter(user=user)

        for car in user_cars:
            if car not in exclude_cars:
                user_availabl_cars.append(car)

        return user_availabl_cars

    def get_user_cars_not_racing(self, user, race):

        cars_not_in_race = []

        player_cars = Car.objects.filter(user=user)
        # iterate through cars see if they are in races

        for car in player_cars:

            try:
                last_car_bet = Bet.objects.filter(car=car).order_by("-pk")[0]
            except IndexError:
                last_car_bet = None

            if last_car_bet:
                if last_car_bet.race.finish:
                    cars_not_in_race.append(car)
            if not last_car_bet:
                cars_not_in_race.append(car)

        return cars_not_in_race


class Race(models.Model):

    is_race24 = models.BooleanField(default=True, db_index=True)
    race_amount = models.DecimalField(max_digits=10, decimal_places=6)
    players = models.PositiveIntegerField(default=0)
    race_hash = models.CharField(max_length=128)
    start = models.DateTimeField(null=True)
    start_coins_price = JSONField(default=dict)
    race_duration_seconds = models.SmallIntegerField(default=ONE_DAY_IN_SECONDS)
    finish = models.DateTimeField(null=True)
    finish_coins_price = JSONField(default=dict)
    coins_performance = JSONField(default=dict)
    cars_performance_at_finish = JSONField(default=dict)
    err_prolonged_game = models.BooleanField(default=False)
    err_prolonged_game_time_delta = models.IntegerField(default=0)
    wins_paid = models.BooleanField(default=False)

    class Meta:
        db_table = "game_races"


class Bet(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    race = models.ForeignKey(Race, on_delete=models.SET_NULL, null=True)
    is_race24 = models.BooleanField()
    coins = JSONField(default=dict)
    bet_amount = models.DecimalField(max_digits=10, decimal_places=6)
    win_amount = models.DecimalField(default=0, max_digits=10, decimal_places=6)
    win_bet_paid = models.BooleanField(default=False)
    win_points = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "game_bets"

    def get_user_total_bets(user, race, race24=False):

        if race24:
            bets = Bet.objects.filter(user=user, race=race, is_race24=True)
        else:
            bets = Bet.objects.filter(user=user, race=race, is_race24=False)

        cars = []

        total_bets = 0
        for bet in bets:
            total_bets += float(bet.bet_amount)
            if bet.car not in cars:
                cars.append(bet.car)

        return total_bets, len(cars)

    def place_bet(user, car, race, coins, bet_amount, is_race24=False):

        if is_race24:

            try:
                # XXX TODO this is not how you do check exists
                check_exists = Bet.objects.get(
                    user=user, car=car, race=race, is_race24=True
                )
            except Bet.DoesNotExist:
                check_exists = False

        else:

            try:
                # XXX TODO this is not how you do check exists
                check_exists = Bet.objects.get(
                    user=user, car=car, race=race, is_race24=False
                )
            except Bet.DoesNotExist:
                check_exists = False

        if check_exists:
            # XXX TODO this is not how you do check exists
            return False

        if is_race24:
            bet = Bet.objects.create(
                user=user,
                car=car,
                race=race,
                coins=coins,
                bet_amount=bet_amount,
                is_race24=True,
            )
        else:
            bet = Bet.objects.create(
                user=user,
                car=car,
                race=race,
                coins=coins,
                bet_amount=bet_amount,
                is_race24=False,
            )

        return bet


class RaceIndexer(models.Model):

    bounty_index = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "game_race_indexer"


class RaceRegistration(models.Model):

    race_type = models.SmallIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    coins = JSONField(default=dict)
    bet = models.ForeignKey(Bet, on_delete=models.PROTECT, null=True)
    is_race24 = models.BooleanField()
    bet_request_fullfiled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "game_race_registrations"


class Notification(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    module = models.CharField(max_length=128)
    message = models.CharField(max_length=512)
    is_new = models.BooleanField(default=True)
    seen_by_user_on = models.DateTimeField(null=True)

    class Meta:
        db_table = "game_notifications"
