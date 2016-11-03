from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.context_processors import csrf
from models import Game
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# Create your views here.
def login(request):
    """
    Write your login view here
    :param request:
    :return:
    """
    # Method=POST then validate user's login details, authenticate and redirect to games page
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if form.is_valid():
            user = authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect(games)
    # Method = GET then display log in form
    args = {}
    args.update(csrf(request))
    args['form'] = AuthenticationForm()
    return render(request, 'login.html', args)


def logout(request):
    """
    write your logout view here
    :param request:
    :return:
    """
    auth.logout(request)
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
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
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
    context = {'my_created_games': my_created_games,
               'open_games': open_games,
               'playing_games': playing_games,
               'concluded_games': concluded_games}
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
