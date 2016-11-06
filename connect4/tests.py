from django.test import TestCase
from connect4.models import Game
from django.contrib.auth.models import User


# Create your tests here.
class GameTestCase(TestCase):
    def setUp(self):
        self.player1 = User(username="c1",
                            first_name="chi",
                            last_name="nguyen")
        self.player1.save()

        self.game = Game(player1=self.player1)
        self.game.save()

    def testGameCreated(self):
        self.assertEqual(str(self.game), 'Join now to play chi')

    def testGameJoined(self):
        player2 = User(username="c2",
                       first_name="chris",
                       last_name="adam")
        player2.save()
        self.game.join_up(player2)
        self.assertEqual(str(self.game), 'chi nguyen vs chris adam')

    def testGameMadeMove(self):
        self.assertTrue(self.game.make_move(player=self.player1, row=5, column=0))
        coin = self.game.last_move
        self.assertEqual(str(coin), 'chi to row 5 and col 0')