import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from ioi.game.models import Race, RacingTeam, TeamMember
from ioi.helpers.generic import file_notification
from ioi.helpers.race import calculate_leaderboard_cars, calculate_leaderboard_teams
from .models import Profile, Like, Affiliate


@login_required
def teams_view(request):

    # Initiate extended user profile

    user = request.user
    profile = Profile.objects.get(user=user)

    # Load teams and the user team membership
    available_teams = RacingTeam.objects.all()

    team_membership = TeamMember.objects.filter(user=request.user)
    if team_membership:
        team_membership = team_membership[0]

    response = render(
        request=request,
        context={
            "user": user,
            "profile": profile,
            "available_teams": available_teams,
            "team_membership": team_membership,
        },
        template_name="teams.html",
    )
    return response


@login_required
def join_team(request, team_pk):

    print("join team")

    # This is a public profile for the user
    user = request.user
    profile = Profile.objects.get(user=user)

    team = RacingTeam.objects.get(pk=team_pk)

    # XXX TODO should not be able to join the team i'm already in

    # Delete existing membership
    TeamMember.objects.filter(user=request.user).delete()
    TeamMember.objects.create(user=request.user, team=team)

    # Charge user the membership fee
    profile.credit -= Decimal(team.cost_to_join_in)
    profile.save()

    # Notification
    notif_message = (
        "Your credit was deducted by -$"
        + str(team.cost_to_join_in)
        + " for joining the "
        + team.name
        + " racing team."
    )
    file_notification(user, "join_team", notif_message, send_email=False)

    return HttpResponseRedirect("/teams/")


@login_required
def profile_view(request, nickname=None, like=None):

    print("profile view", nickname, like)

    if not nickname:
        profile = get_object_or_404(Profile, user=request.user)
        user = profile.user
        nickname = profile.user.nickname
    else:
        user = get_object_or_404(get_user_model(), nickname=nickname)
        nickname = user.nickname
        profile = Profile.objects.get(user=user)

        if user == request.user and not like:
            return HttpResponseRedirect("/profile/")

    if like:

        new_like, created = Like.objects.get_or_create(user=request.user, liked=user)
        profile.likes += 1
        profile.save()

        if not created:
            # the user already liked this profile before..
            print("already liked")
        else:
            message = "User " + request.user.nickname + " just became a fan of yours."
            message += " You have now " + str(profile.likes) + " devouted fans."
            file_notification(user, "buy_cars", message, send_email=False)

    is_favorited = Like.objects.filter(user=request.user, liked=profile.user).count()

    liked_by_users = Like.objects.filter(liked=profile.user)
    number_of_likes = liked_by_users.count()

    profile_liked_users = profile.user.like_set.all()
    i_liked_users = request.user.like_set.all()

    affiliates = request.user.affiliate_set.all()

    response = render(
        request=request,
        context={
            "profile": profile,
            "is_favorited": is_favorited,
            "nickname": nickname,
            "number_of_likes": number_of_likes,
            "liked_by_users": liked_by_users,
            "i_liked_users": i_liked_users,
            "profile_liked_users": profile_liked_users,
            "affiliates": affiliates,
        },
        template_name="profile.html",
    )
    return response


@login_required
def leaderboard_view(request, race_type=None, unit=None, stat=None):

    print("leaderboard")

    # This is a public profile for the user
    user = request.user
    profile = Profile.objects.get(user=user)

    print("leaderboard view")
    print("race_type", race_type, "unit", unit, "stat", stat)

    # Define query date ranges....

    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day
    current_hour = today.hour

    last_month = current_month - 1
    if last_month == 0:
        last_month = 12

    last_year = current_year - 1

    if current_month == 1:
        last_month = 12
        last_year = current_year - 1

    query_year = current_year
    query_month = current_month

    if stat == "current":
        # means the current month
        query_month = current_month
        query_year = current_year

    if stat == "last":
        # means the last month
        query_month = last_month
        query_year = last_year

    # Query races for the selected date range
    races = []
    races24 = []

    if stat == "current" or stat == "last":
        # XXX todo add caching over here....
        races = Race.objects.filter(
            start__year=query_year,
            start__month=query_month,
            players__gte=1,
            wins_paid=True,
            is_race24=False,
        )
        races24 = Race.objects.filter(
            start__year=query_year,
            start__month=query_month,
            players__gte=1,
            wins_paid=True,
            is_race24=True,
        )

    ##############################################################################################################
    # XXX TODO DELETETHIS these two the today and yesterday are only temporarily and should be deleted......
    ##############################################################################################################
    if stat == "today":
        races = Race.objects.filter(
            start__year=current_year,
            start__month=current_month,
            start__day=current_day,
            players__gte=1,
            wins_paid=True,
            is_race24=False,
        )
        races24 = Race.objects.filter(
            start__year=current_year,
            start__month=current_month,
            start__day=current_day,
            players__gte=1,
            wins_paid=True,
            is_race24=True,
        )
    if stat == "yesterday":
        races = Race.objects.filter(
            start__year=current_year,
            start__month=current_month,
            start__day=current_day - 1,
            players__gte=1,
            wins_paid=True,
            is_race24=False,
        )
        races24 = Race.objects.filter(
            start__year=current_year,
            start__month=current_month,
            start__day=current_day - 1,
            players__gte=1,
            wins_paid=True,
            is_race24=True,
        )
    ####################################################################################

    print("races", len(races))
    print("races24", len(races24))
    print("unit", unit)

    # Calculate the leaderboard

    leaderboard_cars = []

    if unit == "players":

        if int(race_type) == 3:
            leaderboard_cars = calculate_leaderboard_cars(
                leaderboard_type="cars", races=races
            )

        if int(race_type) == 24:
            leaderboard_cars = calculate_leaderboard_cars(
                leaderboard_type="cars", races24=races24
            )

    leaderboard_teams = []

    if unit == "teams":

        if int(race_type) == 3:
            leaderboard_teams = calculate_leaderboard_teams(
                leaderboard_type="leaderboard_teams", races=races
            )
        if int(race_type) == 24:
            leaderboard_teams = calculate_leaderboard_teams(
                leaderboard_type="leaderboard_teams", races24=races24
            )

    # Working out winners results....

    winners = {}

    if unit == "winners":

        # Calculate yesterday winner

        today = timezone.now()
        yesterday = today - datetime.timedelta(days=1)

        if int(race_type) == 3:
            races = Race.objects.filter(
                start__gt=yesterday,
                finish__lt=today,
                players__gte=1,
                wins_paid=True,
                is_race24=False,
            )

        if int(race_type) == 24:
            races = Race.objects.filter(
                start__gt=yesterday,
                finish__lt=today,
                players__gte=1,
                wins_paid=True,
                is_race24=True,
            )

        leaderboard_cars = calculate_leaderboard_cars(
            leaderboard_type="cars", races=races
        )

        if leaderboard_cars:

            winners["last_day"] = leaderboard_cars[0]

            winners["last_day"]["meta"] = {"yesterday": yesterday}

        print("calculated yesterday winner")
        print("yesterday was", yesterday)
        # print("winners last_day", winners["last_day"])
        # print("winners last_day meta", winners["last_day"]["meta"])

        # Calculate last week winner

        some_day_last_week = timezone.now().date() - datetime.timedelta(days=7)
        monday_of_last_week = some_day_last_week - datetime.timedelta(
            days=(some_day_last_week.isocalendar()[2] - 1)
        )
        monday_of_this_week = monday_of_last_week + datetime.timedelta(days=7)

        if int(race_type) == 3:
            races = Race.objects.filter(
                start__gte=monday_of_last_week,
                finish__lt=monday_of_this_week,
                is_race24=False,
            )

        if int(race_type) == 24:
            races = Race.objects.filter(
                start__gte=monday_of_last_week,
                finish__lt=monday_of_this_week,
                is_race24=True,
            )

        leaderboard_cars = calculate_leaderboard_cars(
            leaderboard_type="cars", races=races
        )

        if leaderboard_cars:
            winners["last_week"] = leaderboard_cars[0]
        else:
            winners["last_week"] = {}

        winners["last_week"]["meta"] = {
            "some_day_last_week": some_day_last_week,
            "monday_of_last_week": monday_of_last_week,
            "monday_of_this_week": monday_of_this_week,
        }

        print("calculated last_week winner")
        print("some_day_last_week", some_day_last_week)
        print("monday_of_last_week", monday_of_last_week)
        print("monday_of_this_week", monday_of_this_week)

        print("winners last_week", winners["last_week"])
        print("winners last_week meta", winners["last_week"]["meta"])

        # Calculate last month winner

        today = datetime.date.today()
        last_month_finishes = today.replace(day=1)
        last_month_starts = last_month_finishes - datetime.timedelta(days=1)

        if int(race_type) == 3:
            races = Race.objects.filter(
                start__gte=last_month_starts,
                finish__lt=last_month_finishes,
                is_race24=False,
            )

        if int(race_type) == 24:
            races = Race.objects.filter(
                start__gte=last_month_starts,
                finish__lt=last_month_finishes,
                is_race24=True,
            )

        leaderboard_cars = calculate_leaderboard_cars(
            leaderboard_type="cars", races=races
        )

        if leaderboard_cars:
            winners["last_month"] = leaderboard_cars[0]
        else:
            winners["last_month"] = {}

        winners["last_month"]["meta"] = {
            "today": today,
            "last_month_finishes": last_month_finishes,
            "last_month_starts": last_month_starts,
        }

        print("winners last_month", winners["last_month"])
        print("winners last_month meta", winners["last_month"]["meta"])

        # Calculate my personal position

        ########################################################################################################################
        # XXX THIS IS WHAT IT REALLY SHOULD BE..
        # today = datetime.date.today()
        # last_month_finishes = today.replace(day=1)
        # last_month_starts = last_month_finishes - datetime.timedelta(days=1)
        # if int(race_type) == 3:
        #     races = Race.objects.filter(start__gte=last_month_starts, finish__lt=last_month_finishes, is_race24=False)
        # if int(race_type) == 24:
        #     races = Race.objects.filter(start__gte=last_month_starts, finish__lt=last_month_finishes, is_race24=True)
        ########################################################################################################################
        # XXX TODO DELETETHIS IS ONLY TEMPORARILY
        today = timezone.now()
        yesterday = today - datetime.timedelta(days=1)
        if int(race_type) == 3:
            races = Race.objects.filter(
                start__gt=yesterday,
                finish__lt=today,
                players__gte=1,
                wins_paid=True,
                is_race24=False,
            )
        if int(race_type) == 24:
            races = Race.objects.filter(
                start__gt=yesterday,
                finish__lt=today,
                players__gte=1,
                wins_paid=True,
                is_race24=True,
            )
        ################################################################################

        leaderboard_cars = calculate_leaderboard_cars(
            leaderboard_type="cars", races=races
        )

        print("leaderboard_cars", leaderboard_cars)

        # XXX Calculate my team position

        # XXX working on this currently....

    response = render(
        request=request,
        context={
            "profile": profile,
            "race_type": race_type,
            "unit": unit,
            "stat": stat,
            "current_year": current_year,
            "current_month": current_month,
            "current_day": current_day,
            "current_hour": current_hour,
            "last_month": last_month,
            "last_year": last_year,
            "query_year": query_year,
            "query_month": query_month,
            "races": races,
            "race24": races24,
            "winners": winners,
            "leaderboard_cars": leaderboard_cars,
            "leaderboard_teams": leaderboard_teams,
        },
        template_name="leaderboard.html",
    )
    return response


def register_view(
    request, backend="django.contrib.auth.backends.ModelBackend", affiliate_slug=None
):

    if affiliate_slug:

        invite_from_user = get_object_or_404(Profile, affiliate_slug=affiliate_slug)
        invite_from_user = invite_from_user.user
        # print("invite_from_user", invite_from_user)

    if request.POST:

        print(request.POST)

        email = request.POST["email"]
        nickname = request.POST["usrnm"]
        password = request.POST["psw"]
        affiliate_slug = request.POST.get("affiliate_slug")
        if affiliate_slug == "None":
            affiliate_slug = None

        user = get_user_model().objects.create(nickname=nickname, email=email)
        user.set_password(password)
        user.save()

        login(request, user=user, backend=backend)

        profile = Profile.objects.get(user=user)
        profile.credit = Decimal(20000)
        profile.save()

        # Create affiliate
        if affiliate_slug:

            print("affiliate_slug", type(affiliate_slug), affiliate_slug)

            affiliate_user = Profile.objects.get(affiliate_slug=affiliate_slug).user

            new_affiliate, created = Affiliate.objects.get_or_create(
                user=affiliate_user, affiliate=request.user
            )
            if not created:
                # the user already liked this picture before
                print("already an affiliate")

            message = (
                "Your affiliate "
                + user.nickname
                + " just joined in. Your team is growing!"
            )
            file_notification(
                affiliate_user, "affiliate_reg", message, send_email=False
            )

        # Redirect to a success page.
        return HttpResponseRedirect("/")

    response = render(
        request=request,
        context={"affiliate_slug": affiliate_slug},
        template_name="register.html",
    )
    return response
