from flask import Blueprint, request, json, abort
from transcendentserver.models import User, Session, Lobby
from transcendentserver.errors import UserDoesNotExist
from transcendentserver.extensions import db, api
from transcendentserver.controls import matchmaking
from transcendentserver.constants import HTTP, LOBBY
from transcendentserver.lib.npid import NPID

from flask_restful import Resource

from functools import wraps

# TODO: Write migration code if David wants to go that way.


client = Blueprint('client', 'transcendentserver')

def json_status(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if not result:
                result = json.dumps({'success' : True})
            return result
        except Exception, e:
            # TODO: Replace with proper debug logging
            return json.dumps({'success' : False, 'message' : e.message})
    return wrapper

def get_session_or_abort():
    '''
    Arguments:
        None
    Returns:
        Session: Valid Session

    Checks the request for the 'auth' parameter and, if it contains one,
    validates it against the sessions database.
    If at any point the session is not found or is invalid, abort the
    connection with the unauthorized status code.
    '''

    session_id = request.values.get('auth')
    if not session_id: 
        abort(HTTP.UNAUTHORIZED)

    session = Session.get_if_active(session_id)
    if not session: 
        abort(HTTP.UNAUTHORIZED)

    return session

class Login(Resource):
    def post(self):
        name, password = (request.form.get('username'), 
                                         request.form.get('password'))
        current_user = User.find(name)

        if current_user and \
                current_user.check_password(password):
            Session.delete_user_sessions(current_user.id)
            new_session = Session.create_session(current_user)
            return {'access_code' : new_session.id}, 200
        return {'success' : False, 'access_code' : None}, HTTP.UNAUTHORIZED

api.add_resource(Login, '/v1/login')

@client.route('/login', methods=('GET', 'POST'))
def auth_login():
    name, password = request.form.get('username'), request.form.get('password')
    current_user = User.find(name)

    if not current_user:
        return json.dumps({'success': False, 'access_code': None})

    if current_user and \
            current_user.check_password(password):
        Session.delete_user_sessions(current_user.id)
        
        new_session = Session.create_session(current_user)
        return json.dumps(
           {'success': True,
            'access_code' : new_session.id
           })
    return json.dumps(
            {'success' : False,
             'access_code' : None
            })

@client.route('/logout/')
def logout(session_id):
    session = get_session_or_abort()
    
    if not session:
        return json.dumps({'success' : False})
    db.session.delete(session)
    return json.dumps({'success' : True})

@client.route('/server/find')
@json_status
def find_game():
    session = get_session_or_abort()
    game_mode = request.args.get('game_mode')
    if not game_mode: return abort(400)
    possible_lobbies = matchmaking.find_games(game_mode)
    server_count = possible_lobbies.count()
    server_list = [
        { 'id' : lobby.id.hex()
        , 'host-GUID' : lobby.host_guid
        } for lobby in possible_lobbies]
    return json.dumps(
        { 'server-count' : server_count
        , 'server-list' : server_list
        , 'success' : True
        })

@client.route('/server/host')
def host_game():
    session = get_session_or_abort()
    host_guid, game_mode = (request.args.get('guid'), 
                            request.args.get('game_mode'))
    max_players = request.args.get('max_players', LOBBY.MAX_PLAYERS_DEFAULT)

    if not (host_guid and game_mode):
        return abort(400)

    new_lobby = Lobby.create_lobby(host_guid, game_mode, session.user_id, max_players)
    return json.dumps({'success' : True, 'id' : new_lobby.id.hex()})

@client.route('/server/renew')
@json_status
def renew_game():
    session = get_session_or_abort()
    lobby_id = request.args.get('id')

    if not lobby_id:
        return abort(400)

    game = Lobby.get(lobby_id)

    if not game: 
        return json.dumps({'success' : False})

    if session.user.hosts_lobby(game):
        game.renew()
        return json.dumps({'success' : True})

    return json.dumps({'success' : False})

@client.route('/server/remove', methods=('GET', 'POST'))
@json_status
def delete_game():
    session = get_session_or_abort()
    lobby_id = request.values.get('id')

    if not lobby_id:
        abort(400)

    lobby = Lobby.get(lobby_id)
    if not lobby: return json.dumps({'success' : False})

    if session.user.hosts_lobby(lobby):
        lobby.delete()
        return json.dumps({'success' : True})
    return json.dumps({'success' : False})

@client.route('/server/migrate')
@json_status
def migrate():
    print
    print 'MIGRATION'
    print
    print request.args.get('auth')
    # I am dubious about this specification. There is a case where if someone
    # hacked the cert of the client, one could migrate all servers as a kind
    # of DoS attack.
    session = get_session_or_abort()

    print session

    lobby_id, new_host_guid = (request.values.get('id'),
                                 request.values.get('guid'))
    print lobby_id, new_host_guid
    lobby = Lobby.get(NPID(hex=lobby_id))
    print lobby
    if not lobby: return json.dumps({'success' : False,
                                     'message': 'Lobby not found'})
    lobby.change_host(session.user, new_host_guid)
    return json.dumps({'success' : True})
    

@client.route('/account/ship/add')
@json_status
def ship_add():
    return None #session_id
