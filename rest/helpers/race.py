from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ioi.game.models import Car, Bet, RaceIndexer
from ioi.game.models import TeamMember
from ioi.game.models import ONE_DAY_IN_SECONDS

from ioi.profiles.models import Profile
from .crypto import calculate_coins_performance


RACES_ORDER = settings.RACES_ORDER


def calculate_race_due_in_seconds(race):

    race_due_to_finish = race.start + timedelta(seconds=race.race_duration_seconds)
    race_due_in_seconds = (race_due_to_finish - timezone.now()).total_seconds()

    return race_due_in_seconds


def get_player_position(players_score, player):

    position = 1

    s = [
        (k, players_score[k])
        for k in sorted(players_score, key=players_score.get, reverse=True)
    ]
    for k, v in s:
        print(k, v)
        if k == player.pk:
            break
        position += 1

    return position


def calculate_cars_score(race, coins_performance="", is_race24=False):

    cars_score = {}

    if is_race24:
        bets = Bet.objects.filter(race=race, is_race24=True)
    else:
        bets = Bet.objects.filter(race=race, is_race24=False)

    if not coins_performance:
        coins_performance = calculate_coins_performance(
            race.start_coins_price, race.finish_coins_price
        )

    for bet in bets:

        car_cummulative_score = 0

        bet_coins = bet.coins

        print("* bet.coins", type(bet_coins), bet_coins)

        for coin in bet.coins:

            print(" - coin", coin)

            for x in coins_performance:
                if x["symbol"] == coin["symbol"]:
                    coin_performance = x["percent"]

            score = float(coin_performance) / 100 * float(coin["bet"])
            score *= 10

            print("coin_performance", type(coin_performance), coin_performance)
            print("coin_bet", type(coin["bet"]), coin["bet"])
            print(
                "player",
                bet.user.pk,
                coin["symbol"],
                "bet",
                coin["bet"],
                "coin_performance",
                coin_performance,
                "score",
                score,
            )

            car_cummulative_score += score

        print("Car", bet.car, car_cummulative_score)
        cars_score[bet.car] = car_cummulative_score

    print("cars_score", cars_score)

    return cars_score


def get_race_statistics(race, calculated_coins_performance):

    is_race24 = False

    if race.is_race24:
        is_race24 = True

    cars_score = calculate_cars_score(
        race, coins_performance=calculated_coins_performance, is_race24=is_race24
    )

    # Enhance racing data

    cars_score_sorted = {}

    s = [
        (k, cars_score[k]) for k in sorted(cars_score, key=cars_score.get, reverse=True)
    ]
    for k, v in s:
        print(k, v)
        cars_score_sorted[k] = v

    print("cars_score_sorted", cars_score_sorted)

    race_due_in_seconds = calculate_race_due_in_seconds(race)
    race_progression_seconds = race.race_duration_seconds - race_due_in_seconds
    race_progression_percent = (
        race_progression_seconds / race.race_duration_seconds * 100
    )
    race_progression_percent = round(race_progression_percent, 2)

    print("race_due_in_seconds", race_due_in_seconds)
    print("race_progression_seconds", race_progression_seconds)
    print("race_progression_percent", race_progression_percent)

    cars_performance = []

    cars_score_sorted_map = []
    for p in cars_score_sorted:
        cars_score_sorted_map.append(p)

    print("cars_score", cars_score)

    for car in cars_score:

        score = cars_score[car]
        relative_position = race_progression_percent + score * 10

        if relative_position > 99.9:
            relative_position = 99.9

        if is_race24:
            bet = Bet.objects.get(race=race, car=car, is_race24=True)
        else:
            bet = Bet.objects.get(race=race, car=car, is_race24=False)

        pl = {
            "bet": bet,
            "bet_pk": bet.pk,
            "race": race,
            "race_pk": race.pk,
            "car": car,
            "car_pk": car.pk,
            "score": round(score, 2),
            "roi": "ROI% is score really",
            "relative_position": relative_position,
            "time_progression_percent": race_progression_percent,
        }
        cars_performance.append(pl)

    cars_performance_sorted = sorted(cars_performance, key=lambda i: (i["score"]))
    cars_performance_sorted.reverse()

    # calculate players points

    car_position_in_the_race = 0

    cars_performance_sorted_with_points = []

    for pl in cars_performance_sorted:

        points = get_points_for_position(car_position_in_the_race)
        pl["points"] = points
        pl["car_position_in_the_race"] = car_position_in_the_race
        cars_performance_sorted_with_points.append(pl)
        car_position_in_the_race += 1

    cars_performance_sorted = cars_performance_sorted_with_points

    return cars_performance_sorted_with_points


def estimate_time_until_race_start_seconds(
    race_type, current_race_finishing_in_seconds
):

    ri = RaceIndexer.objects.get(pk=1)
    bounty_index = ri.bounty_index

    mixed_order_races = RACES_ORDER + RACES_ORDER

    following_races = mixed_order_races[bounty_index:]

    races_ahead = 0

    for i in following_races:
        if i == race_type:
            # print("found index", i, races_ahead)
            break
        races_ahead += 1

    if races_ahead == 0:

        first = 0

        for i in following_races:
            if i == race_type:
                if first:
                    # print("found index", i, races_ahead)
                    break
                first += 1
            races_ahead += 1

    est_time_seconds = current_race_finishing_in_seconds
    est_time_seconds += (races_ahead - 1) * settings.RACES_DURATION_SECONDS
    est_time_seconds += (races_ahead - 2) * settings.DELAY_BETWEEN_RACES

    if est_time_seconds < 0:
        est_time_seconds = 0

    return est_time_seconds


def get_time_remaining_to_current_race_to_finish(race):

    current_race_finishing_at = race.start + timedelta(
        seconds=race.race_duration_seconds
    )

    # 24hrs race really is 23hrs + 1hr pause
    if race.is_race24:
        current_race_finishing_at = current_race_finishing_at - timedelta(hours=1)

    current_race_finishing_in_seconds = (
        current_race_finishing_at - timezone.now()
    ).total_seconds()

    if current_race_finishing_in_seconds < 0:
        current_race_finishing_in_seconds = 0

    # check if the race is on or cancelled
    is_cancelled = False
    longetivity = abs((race.start - timezone.now()).total_seconds())
    if race.start and race.players == 0 and longetivity > 20:
        is_cancelled = True

    return current_race_finishing_in_seconds, current_race_finishing_at, is_cancelled


def get_time_remaining_to_the_next_race24(race24):

    # Calculate time remaining to the next 24 hours race

    next_race24_starting_at = race24.start + timedelta(seconds=ONE_DAY_IN_SECONDS)
    next_race24_starting_in_seconds = (
        next_race24_starting_at - timezone.now()
    ).total_seconds()
    next_race24_starting_in_seconds = round(next_race24_starting_in_seconds, 1)
    next_race24_starting_in_seconds = abs(next_race24_starting_in_seconds)

    current_race24_finishing_in_seconds = next_race24_starting_in_seconds - 3600

    return current_race24_finishing_in_seconds, next_race24_starting_in_seconds


def get_points_for_position(player_position_in_race):

    points = 0

    if player_position_in_race == 0:
        points = 25

    if player_position_in_race == 1:
        points = 18

    if player_position_in_race == 2:
        points = 15

    if player_position_in_race == 3:
        points = 12

    if player_position_in_race == 4:
        points = 10

    if player_position_in_race == 5:
        points = 8

    if player_position_in_race == 6:
        points = 6

    if player_position_in_race == 7:
        points = 4

    if player_position_in_race == 8:
        points = 2

    if player_position_in_race == 9:
        points = 1

    return points


def serialize_cars_performance(cars_performance):

    cars_performance_ready_for_serialization = []

    for x in cars_performance:

        # we still do have these elements pk-s in there so we don't necesarily need objects in there...
        stat = {
            "bet_pk": x["bet_pk"],
            "race_pk": x["race_pk"],
            "car_pk": x["car_pk"],
            "score": x["score"],
            "roi": "ROI% is score really",
            "relative_position": x["relative_position"],
            "time_progression_percent": x["time_progression_percent"],
            "points": x["points"],
            "car_position_in_the_race": x["car_position_in_the_race"],
        }
        cars_performance_ready_for_serialization.append(stat)

    return cars_performance_ready_for_serialization


# XXX this is a heavy duty application and should be cached
def calculate_team_table(team):

    team_score = []

    print("calculating team score", team)

    all_team_members = TeamMember.objects.filter(team=team.team)

    for team_member in all_team_members:
        team_member_profile = Profile.objects.get(user=team_member.user)
        team_score.append(
            {
                "user": team_member.user,
                "total_win_points": team_member_profile.total_win_points,
            }
        )
        print(
            " -",
            team_member_profile.total_win_points,
            team_member,
            team_member.user,
            team_member_profile,
        )

    team_score_sorted = sorted(team_score, key=lambda i: (i["total_win_points"]))
    team_score_sorted.reverse()

    return team_score_sorted


# XXX this is a heavy duty application and should be cached
def calculate_team_position(user):

    user_team = TeamMember.objects.get_user_team(user)

    if user_team:

        team_table = calculate_team_table(user_team)

    else:
        team_table = []

    # calculate own position

    position = 0

    user_profile = Profile.objects.get(user=user)

    for t in team_table:

        if t["user"] == user:
            position += 1
            break

        position += 1

    print("**** calculate_team_position")
    print("**** team_table", len(team_table), team_table)
    print("**** your points", user_profile.total_win_points)
    print("**** your position in the team", position)

    return position


# XXX this is a heavy duty application and should be cached
def calculate_leaderboard_cars(leaderboard_type="cars", races=None, races24=None):

    leaderboard_cars = {}

    if races:
        races = races
    if races24:
        races = races24

    if races:

        for race in races:

            print(" - analyzing race", race.pk, "players", race.players, race.start)

            cars_performance = race.cars_performance_at_finish

            for car in cars_performance:

                car_pk = car["car_pk"]
                bet_pk = car["bet_pk"]
                race_pk = car["race_pk"]
                score = float(car["score"])
                points = int(car["points"])
                position = int(car["car_position_in_the_race"])

                print(
                    "\tcar",
                    car_pk,
                    "score",
                    score,
                    "bet_pk",
                    bet_pk,
                    "race_pk",
                    race_pk,
                    "score",
                    score,
                    "points",
                    points,
                )

                if car_pk in leaderboard_cars:

                    if bet_pk not in leaderboard_cars[car_pk]["bet_pk"]:
                        leaderboard_cars[car_pk]["bet_pk"].append(bet_pk)

                    if race_pk not in leaderboard_cars[car_pk]["races"]:
                        leaderboard_cars[car_pk]["races"].append(race_pk)

                    leaderboard_cars[car_pk]["score"] += score
                    leaderboard_cars[car_pk]["points"] += points

                else:
                    leaderboard_cars[car_pk] = {
                        "bet_pk": [bet_pk],
                        "races": [race_pk],
                        "score": score,
                        "points": points,
                    }

                if position == 0:

                    if "wins" in leaderboard_cars[car_pk]:

                        leaderboard_cars[car_pk]["wins"] += 1
                    else:
                        leaderboard_cars[car_pk]["wins"] = 1

    print("len leaderboard_cars", len(leaderboard_cars))

    # add the leaderboard data onto the list so that we can sort it by cars score

    leaderboard_cars_list = []

    for car in leaderboard_cars:
        data = {
            "car_pk": int(car),
            "bet_pk": leaderboard_cars[car]["bet_pk"],
            "races": leaderboard_cars[car]["races"],
            "score": leaderboard_cars[car]["score"],
            "points": leaderboard_cars[car]["points"],
        }

        if "wins" in leaderboard_cars[car]:
            data["wins"] = leaderboard_cars[car]["wins"]
        else:
            data["wins"] = 0

        leaderboard_cars_list.append(data)

    leaderboard_cars_sorted = sorted(leaderboard_cars_list, key=lambda i: (i["points"]))
    leaderboard_cars_sorted.reverse()

    print("leaderboard_cars_sorted", leaderboard_cars_sorted)

    return leaderboard_cars_sorted


# XXX this is a heavy duty application and should be cached
def calculate_leaderboard_teams(leaderboard_type="cars", races=None, races24=None):

    leaderboard_teams = {}

    leaderboard_cars = calculate_leaderboard_cars(
        leaderboard_type="cars", races=races, races24=races24
    )

    print(leaderboard_cars)

    for c in leaderboard_cars:

        car = Car.objects.get(pk=c["car_pk"])
        team_member = TeamMember.objects.get_user_team(car.user)
        points = c["points"]
        score = c["score"]

        players = {}

        if team_member:

            print(
                "player",
                car.user,
                "car",
                car,
                "team",
                team_member.team.name,
                "points",
                points,
            )

            if leaderboard_teams.get(team_member.team.name):

                leaderboard_teams[team_member.team.name]["points"] += points

                players = leaderboard_teams[team_member.team.name]["players"]

                if players.get(car.user):

                    players[car.user] = {
                        "points": players[car.user]["points"] + points,
                        "score": players[car.user]["score"] + score,
                    }

                else:

                    players[car.user] = {"points": points, "score": score}

                leaderboard_teams[team_member.team.name]["players"] = players
                leaderboard_teams[team_member.team.name]["name"] = team_member.team.name

            else:
                leaderboard_teams[team_member.team.name] = {
                    "points": points,
                    "players": {car.user: {"points": points, "score": score}},
                    "name": team_member.team.name,
                }

    print("leaderboard_teams", leaderboard_teams)

    # identify team leaders

    leaders = {}

    for team in leaderboard_teams:

        team_leader_points = 0
        moon_rider_score = -100

        players = leaderboard_teams[team]["players"]

        for p in players:

            points = players[p]["points"]
            score = players[p]["score"]

            if points > team_leader_points:

                if leaders.get(team):
                    leaders[team]["team_leader"] = {p: points}
                else:
                    leaders[team] = {"team_leader": {p: points}}
                    team_leader_points = points

            if score > moon_rider_score:

                if leaders.get(team):
                    leaders[team]["moon_rider"] = {p: score}
                else:
                    leaders[team] = {"moon_rider": {p: score}}
                moon_rider_score = score

    print("leaders", leaders)

    for team in leaders:

        leaderboard_teams[team]["team_leader"] = leaders[team]["team_leader"]

        leaderboard_teams[team]["moon_rider"] = leaders[team]["moon_rider"]

    # trasfer the data so that we can sort by points

    leaderboard_teams_sorted = []

    last_value = 0

    for team in leaderboard_teams:

        if last_value < points:
            leaderboard_teams_sorted.append(leaderboard_teams[team])
        else:
            leaderboard_teams_sorted.insert(0, leaderboard_teams[team])

        last_value = points

        print("team", team, leaderboard_teams[team], leaderboard_teams[team]["points"])

    # sorted results

    leaderboard_teams_sorted = sorted(
        leaderboard_teams_sorted, key=lambda i: (i["points"])
    )
    leaderboard_teams_sorted.reverse()

    print("leaderboard_teams_sorted", leaderboard_teams_sorted)

    return leaderboard_teams_sorted


# XXX this is a heavy duty application and should be cached
def calculate_cars_performance(race):

    # Calculate coins performance

    start_price = race.start_coins_price
    finish_price = race.finish_coins_price

    calculated_coins_performance = calculate_coins_performance(
        start_price, finish_price
    )

    # Recording race statistics

    cars_performance = get_race_statistics(race, calculated_coins_performance)
    print("cars_performance", cars_performance)

    # Serialize cars performance
    cars_performance_serialized = serialize_cars_performance(cars_performance)
    print("cars_performance_serialized", cars_performance_serialized)

    return cars_performance_serialized
