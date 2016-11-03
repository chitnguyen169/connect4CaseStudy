import json
import logging
from channels import Group
from channels.sessions import channel_session
from .models import Game
from django.contrib.auth.models import User

log = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
    # Extract the game from the coin. This expects coin.path to be of the
    # connect4/play/{game_id}/, and finds a Game if the coin path is applicable,
    # and if the Game exists. Otherwise, bails (meaning this is a some other sorts
    # of websocket). So, this is effectively a version of _get_object_or_404.
    game_id = message['path'].strip('/').split('/')[-1]
    game = Game.objects.get(id=game_id)

    log.debug('play made at game=%s, client=%s:%s',
              game_id, message['client'][0], message['client'][1])
    Group('game-'+game_id, channel_layer=message.channel_layer).add(message.reply_channel)
    message.channel_session['game'] = game_id


@channel_session
def ws_receive(message):
    game_id = message.channel_session['game']
    # using game below to write message to db here
    game = Game.objects.get(id=game_id)
    try:
        data = json.loads(message['text'])
    except ValueError:
        return
    if data:
        row = data['row']
        col = data['col']
        status = data['status']
        current_player = User.objects.get(id=data['current_player'])
        log.debug('game=%s, coin placed at row=%s col=%s',
                  game_id, data['row'], data['col'])
        if game.status == 'Concluded':
            raise ValueError('Game already finished!')
        elif game.status == 'Playing' and current_player.id not in [game.player1_id, game.player2_id]:
            raise ValueError("Only current players are allowed to make the move")
        elif not game.coin_set.all() or game.last_move.player != current_player:
            game.make_move(current_player, row, col)
            if status == 'Concluded':
                game.status = 'Concluded'
                game.winner = current_player.username
                game.save()

        else:
            raise ValueError("Can not make 2 moves in a row")
        if game.winner:
            data['winner'] = game.winner
        Group('game-'+game_id, channel_layer=message.channel_layer).send({'text': json.dumps(data)})


@channel_session
def ws_disconnect(message):
    game_id = message.channel_session['game']
    Group('game-'+game_id).discard(message.reply_channel)