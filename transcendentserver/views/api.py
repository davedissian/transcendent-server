from flask import Blueprint, request, json, abort
from flask_restful import Api, Resource, reqparse
from transcendentserver.models import User, Session, Lobby
from transcendentserver.errors import UserDoesNotExist
from transcendentserver.extensions import db
from transcendentserver.controls import matchmaking
from transcendentserver.constants import HTTP, LOBBY
from transcendentserver.lib.npid import NPID

from functools import wraps


class ClientApi(Api):
    def handle_error(self, e):
        # Hijack the response and add a 'success' field to the JSON
        response = super(ClientApi, self).handle_error(e)
        response_data = json.loads(response.get_data())
        response_data[unicode('success')] = False
        response.set_data(json.dumps(response_data))
        return response


api_bp = Blueprint('api', 'transcendentserver')
api = ClientApi(api_bp)


def get_session_or_abort(session_id):
    """
    Checks the request for the 'auth' parameter and, if it contains one,
    validates it against the sessions database. If at any point the session is
    not found or is invalid, abort the connection with the unauthorized status
    code.
    """
    session = Session.get_if_active(session_id)
    if not session: 
        abort(HTTP.UNAUTHORIZED)

    return session


class UserSession(Resource):
    def post(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        password = args['password']
        current_user = User.find(username)

        if not current_user:
            return {'success' : False, 'message' : 'Username does not exist'}, HTTP.UNAUTHORIZED

        if not current_user.check_password(password):
            return {'success' : False, 'message' : 'The password provided is incorrect'}, HTTP.UNAUTHORIZED

        Session.delete_user_sessions(current_user.id)
        new_session = Session.create_session(current_user)
        return {'success' : True, 'auth' : new_session.id}

    def delete(self, username):
        # TODO - is username == auth?
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        args = parser.parse_args()

        session = get_session_or_abort(args['auth'])
        db.session.delete(session)
        return {'success' : True}


class UserShips(Resource):
    def get(self, username):
        # TODO - is auth required?
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        args = parser.parse_args()
        return {'success' : True, 'ship_list' : {'test':'1'}}

    def post(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('design', type=str, required=True)
        args = parser.parse_args()

        print 'Adding ship {0}, name={1}, design {2}'.format(0, args['name'], args['design'])
        return {'success' : True, 'ship_id' : 0}


class UserShip(Resource):
    def put(self, username, ship_id):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        parser.add_argument('name', type=str)
        parser.add_argument('design', type=str)
        args = parser.parse_args()

        print 'Updating ship {0}, name={1}, design={2}'.format(ship_id, args['name'], args['design'])
        return {'success' : True}

    def delete(self, username, ship_id):
        print 'Deleting ship {0} owned by {1}'.format(ship_id, username)
        return {'success' : True}


class Servers(Resource):
    def get(self):
        possible_lobbies = matchmaking.find_games(0)
        server_count = possible_lobbies.count()
        server_list = [
            { 'id' : lobby.id.hex(),
              'host_guid' : lobby.host_guid
            } for lobby in possible_lobbies]
        return { 'count' : server_count,
                 'list' : server_list,
                 'success' : True
               }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        parser.add_argument('guid', type=int, required=True)
        parser.add_argument('max_players', default=LOBBY.MAX_PLAYERS_DEFAULT)
        args = parser.parse_args()

        session = get_session_or_abort(args['auth'])
        host_guid = args['guid']
        max_players = args['max_players']

        new_lobby = Lobby.create_lobby(host_guid, 0, session.user_id, max_players)
        return {'success' : True, 'id' : new_lobby.id.hex()}


class Server(Resource):
    def put(self, server_id):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        args = parser.parse_args()

        session = get_session_or_abort(args['auth'])
        game = Lobby.get(server_id)
        if not game: 
            return {'success' : False}

        if session.user.hosts_lobby(game):
            game.renew()
            return {'success' : True}

        return {'success' : False}

    def delete(self, server_id):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, required=True)
        args = parser.parse_args()

        session = get_session_or_abort(args['auth'])
        lobby = Lobby.get(server_id)
        if not lobby:
            return {'success' : False}

        if session.user.hosts_lobby(lobby):
            lobby.delete()
            return {'success' : True}
        return {'success' : False}


# This is deprecated in favour of a more REST api
class ServerMigrate(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth', type=str, required=True)
        self.reqparse.add_argument('id', type=int, required=True)
        self.reqparse.add_argument('guid', type=int, required=True)

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
            return {'success' : False, 'message': 'Lobby not found'}
        lobby.change_host(session.user, new_host_guid)
        return {'success' : True}


api.add_resource(UserSession, '/users/<string:username>/session')
api.add_resource(UserShips, '/users/<string:username>/ships')
api.add_resource(UserShip, '/users/<string:username>/ships/<int:ship_id>')
api.add_resource(Servers, '/servers')
api.add_resource(Server, '/servers/<int:server_id>')
api.add_resource(ServerMigrate, '/server/migrate')
