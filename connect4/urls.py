from django.conf.urls import url
import views

urlpatterns = [
    url(
        r'^login/$',
        views.login
    ),
    url(
        r'^logout/$',
        views.logout
    ),
    url(
        r'^signup/$',
        views.signup
    ),
    url(
        r'^games/$',
        views.games
    ),
    # URL for play view: /connect4/play/{game_id}
    url(
        r'^play/(?P<game_id>\d+)/$',
        views.play
    )
]
