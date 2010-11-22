from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^game/(?P<game_id>[0-9]+)/$', 'seeker.play.game'),
    (r'^game/(?P<game_id>[0-9]+)/guesser/$', 'seeker.play.guesser'),
    (r'^game/(?P<game_id>[0-9]+)/guess/$', 'seeker.play.guess'),
    (r'^game/(?P<game_id>[0-9]+)/quit/$', 'seeker.play.quit'),
    (r'^game/(?P<game_id>[0-9]+)/debug_clues/$', 'seeker.play.debug_clues'),
)