from flask import Blueprint, request, json, abort
from flask_restful import Api, Resource, reqparse
from transcendentserver.models import User, Session, Lobby
from transcendentserver.errors import UserDoesNotExist
from transcendentserver.extensions import db
from transcendentserver.controls import matchmaking
from transcendentserver.constants import HTTP, LOBBY
from transcendentserver.lib.npid import NPID

from functools import wraps


client = Blueprint('client', 'transcendentserver')
api = Api(client)


def json_status(f):
    """
    Call a function and emit any exception raised back to the application
    as a JSON formatted error message.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if not result:
                result = json.dumps({'success' : True})
            return result
        except Exception as e:
            # TODO: Replace with proper debug logging
            return json.dumps({'success' : False, 'message' : str(e)})
    return wrapper


def get_session_or_abort(session_id):
    """
    Checks the request for the 'auth' parameter and, if it contains one,
    validates it against the sessions database. If at any point the session is
    not found or is invalid, abort the connection with the unauthorized status
    code.
    """
    if not session_id: 
        abort(HTTP.UNAUTHORIZED)

    session = Session.get_if_active(session_id)
    if not session: 
        abort(HTTP.UNAUTHORIZED)

    return session


class Login(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True)
        self.reqparse.add_argument('password', type=str, required=True)

    def post(self):
        args = self.reqparse.parse_args()
        name, password = args['username'], args['password']

        current_user = User.find(name)

        if current_user and current_user.check_password(password):
            Session.delete_user_sessions(current_user.id)
            new_session = Session.create_session(current_user)
            return {'success' : True, 'access_code' : new_session.id}, HTTP.OK

        return {'success' : False, 'access_code' : None}, HTTP.UNAUTHORIZED


class Logout(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)

    def post(self):
        args = self.reqparse.parse_args()
        session = get_session_or_abort(args['auth'])
        db.session.delete(session)
        return json.dumps({'success' : True})


class ServerFind(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)
        self.reqparse.add_argument('game_mode', type=int, required=True)

    @json_status
    def get(self):
        args = self.reqparse.parse_args()
        session = get_session_or_abort(args['auth'])
        game_mode = args['game_mode']

        if not game_mode:
            return abort(400)

        possible_lobbies = matchmaking.find_games(game_mode)
        server_count = possible_lobbies.count()
        server_list = [
            { 'id' : lobby.id.hex(),
              'host-GUID' : lobby.host_guid
            } for lobby in possible_lobbies]
        return json.dumps(
            { 'server-count' : server_count,
              'server-list' : server_list,
              'success' : True
            })


class ServerHost(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)
        self.reqparse.add_argument('game_mode', type=int, required=True)
        self.reqparse.add_argument('guid', type=int, required=True)
        self.reqparse.add_argument('max_players', default=LOBBY.MAX_PLAYERS_DEFAULT)

    def post(self):
        args = self.reqparse.parse_args()
        session = get_session_or_abort(args['guid'])
        host_guid, game_mode = args['guid'], args['game_mode']
        max_players = args['max_players']

        if not (host_guid and game_mode):
            return abort(400)

        new_lobby = Lobby.create_lobby(host_guid, game_mode, session.user_id, max_players)
        return json.dumps({'success' : True, 'id' : new_lobby.id.hex()})


class ServerRenew(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)
        self.reqparse.add_argument('id', type=int, required=True)

    @json_status
    def post(self):
        args = self.reqparse.parse_args()
        session = get_session_or_abort(args['auth'])
        lobby_id = args['id']

        if not lobby_id:
            return abort(400)

        game = Lobby.get(lobby_id)

        if not game: 
            return json.dumps({'success' : False})

        if session.user.hosts_lobby(game):
            game.renew()
            return json.dumps({'success' : True})

        return json.dumps({'success' : False})


class ServerDelete(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)
        self.reqparse.add_argument('id', type=int, required=True)

    @json_status
    def post(self):
        args = self.reqparse.parse_args()
        session = get_session_or_abort(args['auth'])
        lobby_id = args['id']

        if not lobby_id:
            abort(400)

        lobby = Lobby.get(lobby_id)
        if not lobby: return json.dumps({'success' : False})

        if session.user.hosts_lobby(lobby):
            lobby.delete()
            return json.dumps({'success' : True})
        return json.dumps({'success' : False})


class ServerMigrate(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)
        self.reqparse.add_argument('id', type=int, required=True)
        self.reqparse.add_argument('guid', type=int, required=True)

    @json_status
    def post(self):
        args = self.reqparse.parse_args()

        print
        print 'MIGRATION'
        print
        print args['auth']

        # I am dubious about this specification. There is a case where if someone
        # hacked the cert of the client, one could migrate all servers as a kind
        # of DoS attack.
        session = get_session_or_abort(args['auth'])

        print session

        lobby_id, new_host_guid = args['id'], args['guid']
        print lobby_id, new_host_guid
        lobby = Lobby.get(NPID(hex=lobby_id))
        print lobby
        if not lobby:
            return json.dumps({'success' : False, 'message': 'Lobby not found'})
        lobby.change_host(session.user, new_host_guid)
        return json.dumps({'success' : True})


api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(ServerFind, '/server/find')
api.add_resource(ServerHost, '/server/host')
api.add_resource(ServerRenew, '/server/renew')
api.add_resource(ServerDelete, '/server/delete')
api.add_resource(ServerMigrate, '/server/migrate')
