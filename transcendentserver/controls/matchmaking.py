from transcendentserver.models import Lobby
from transcendentserver.constants import MATCHMAKING

# TODO: Add support for an offset
def find_games(game_mode, page=0):
    offset = MATCHMAKING.LOBBY_LIST_LIMIT * page
    return Lobby.query\
                .filter_by(mode=game_mode)\
                .offset(offset)\
                .limit(MATCHMAKING.LOBBY_LIST_LIMIT)
