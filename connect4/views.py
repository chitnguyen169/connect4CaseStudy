from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.context_processors import csrf
from models import Game
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import itertools
from collections import Counter
from . import forms


# Create your views here.
def login(request):
    """
    Write your login view here
    :param request:
    :return:
    """
    # If user has not logged out, direct to games page
    if request.session.has_key('username'):
        username = request.session['username']
        return HttpResponseRedirect('/connect4/games/')
    # Else when user logs in (method=POST), store session under username so next time even if user go to log in page,
    #  it will automatically redirect to games page. Else display log in form
    else:
        username = 'not logged in'
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            if form.is_valid():
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    request.session['username'] = username
                    return HttpResponseRedirect('/connect4/games/')
        else:
            form = AuthenticationForm()
        args = {}
        args.update(csrf(request))
        args['form'] = form
        return render(request, 'login.html', args)


def logout(request):
    """
    write your logout view here
    :param request:
    :return:
    """
    try:
        auth.logout(request)
        del request.session['username']
    except:
        pass
    return redirect(login)


def signup(request):
    """
    write your user sign up view here
    :param request:
    :return:
    """
    # If method = POST, then validate form, save user's details to db and redirect to log in page
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(login)
    else:
        form = UserCreationForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render(request, 'signup.html', args)


@login_required(login_url='/connect4/login/')
def games(request):
    """
    Write your view which controls the game set up and selection screen here
    :param request:
    :return:
    """
    # Create a new game
    if request.method == 'POST':
        player1 = request.user
        game = Game(player1=player1)
        game.save()

    my_created_games = Game.objects.all().filter(status='Open', player1=request.user)
    open_games = Game.objects.all().filter(status='Open').exclude(player1=request.user)
    playing_games = Game.objects.all().filter(Q(status='Playing'),
                                              Q(player1=request.user) | Q(player2=request.user))
    concluded_games = Game.objects.all().filter(Q(status='Concluded'),
                                                Q(player1=request.user) | Q(player2=request.user))
    total_games = len(concluded_games)
    total_wins = len(concluded_games.filter(winner=request.user))
    total_draws = len(concluded_games.filter(winner='Draw'))
    total_loses = total_games - total_wins - total_draws
    context = {'my_created_games': my_created_games,
               'open_games': open_games,
               'playing_games': playing_games,
               'concluded_games': concluded_games,
               'total_games': total_games,
               'total_wins': total_wins,
               'total_draws': total_draws,
               'total_loses': total_loses}
    return render(request, 'game.html', context)


@login_required(login_url='/connect4/login/')
def play(request, game_id):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request, game_id:
    :return:
    """
    # Get game object by id
    game = Game.objects.get(id=game_id)
    if game.player1 != request.user:
        game.join_up(request.user)

    coin_set = game.coin_set
    player_turns = [coin.player_id for coin in game.coin_set.all()]
    rows = [coin.row for coin in game.coin_set.all()]
    cols = [coin.column for coin in game.coin_set.all()]
    last_move = game.last_move if len(game.coin_set.all()) else None
    context = {
        'game': game,
        'coin_set': coin_set,
        'player_turns': player_turns,
        'rows': rows,
        'cols': cols,
        'last_move': last_move
    }
    return render(request, 'play.html', context)


@login_required(login_url='/connect4/login/')
def settings(request):
    # Get current username from session
    username = request.session['username']
    if request.method == 'POST':
        # as request.POST is immutable, we don't want user to update username but want to send username as well.
        # so need to create a copy data and then pass in username.
        data = request.POST.copy()
        data['username'] = username
        form = forms.UserUpdateForm(data=data, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(settings)
    else:
        form = forms.UserUpdateForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render(request, 'settings.html', args)