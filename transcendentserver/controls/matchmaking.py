from transcendentserver.models import Game
from transcendentserver.constants import MATCHMAKING

# TODO: Add support for an offset
def find_games(game_mode):
    return Game.query.filter_by(mode=game_mode).limit(MATCHMAKING.GAME_LIST_LIMIT)
