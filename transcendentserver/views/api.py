from flask import Blueprint, request, json, abort
from transcendentserver.models import User, Session
from transcendentserver.errors import UserDoesNotExist
from transcendentserver.extensions import db, api
from transcendentserver.controls import matchmaking
from transcendentserver.constants import HTTP

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
        except Exception:
            return json.dumps({'success' : False})
    return wrapper

def session_from_args_or_abort(args):
    session_id = request.args.get('auth')
    if not sesion_id: abort(HTTP.UNAUTHORIZED)
    session = Session.get_if_active(session_id)
    if not session: abort(HTTP.UNAUTHORIZED)
    return session

class Login(Resource):
    def post(self):
        name, password, refresh_token = (request.values.get('username'), 
                                         request.values.get('password'), 
                                         request.values.get('refresh_token'))
        print name
        current_user = User.find(name)
        print current_user
        if current_user and \
                current_user.check_password(password):
            Session.delete_user_sessions(current_user.id)
            new_session = Session.create_session(current_user)
            return {'access_code' : new_session.id}, 201
        return {'success' : False, 'access_code' : None}, 403

api.add_resource(Login, '/v1/login')

@client.route('/login', methods=('GET', 'POST'))
def auth_login():
    name, password, refresh_key = request.args.get('username'), request.args.get('password'), request.args.get('refresh_key')
    current_user = User.find(name)

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

@client.route('/logout/<session>')
def logout(session_id):
    try:
        session = Session.get_if_active(session_id)
    except Exception, e:
        return str(e), 200
    
    if not session:
        return json.dumps({'success' : False})
    db.session.delete(session)
    return json.dumps({'success' : True})

@client.route('/server/find')
def find_game():
    session = session_from_args_or_abort(request.args)
    game_mode = request.args.get('game_mode')
    if not game_mode: return abort(400)
    possible_games = matchmaking.find_games(game_mode)
    server_count = possible_games.count()
    server_list = [
        { 'host-username' : 'Is this needed?'
        , 'GUID' : game.id
        } for game in possible_games]
    return json.dumps(
        { 'server-count' : server_count
        , 'server-list' : server_list
        })

@client.route('/server/host')
def host_game():
    session_id, host_guid, game_mode = request.args.get('auth'), request.args.get('guid'), request.args.get('game_mode')
    max_players = request.args.get('max_players')

    if not (session_id and host_guid and game_mode and max_players):
        return abort(400)

    session = Session.get_if_active(session_id)
    if session:
        new_game = Game.create_game(game_id, game_mode, session.user_id, max_players)
        return json.dumps({'success' : True, 'id' : new_game.id})
    return json.dumps({'success' : False})

@client.route('/server/renew')
@json_status
def renew_game():
    session_id, game_id = request.args['auth'], request.args['id']
    game = Game.get(game_id)
    if not game: return json.dumps({'success' : False})
    session = Session.get_if_active(session_id)
    if session and session.user.hosts_game(game):
        game.renew()
        return json.dumps({'success' : True})
    return json.dumps({'success' : False})

@client.route('/server/delete')
@json_status
def delete_game():
    session_id, game_id = request.args['auth'], request.args['id']
    game = Game.get(game_id)
    if not game: return json.dumps({'success' : False})
    session = Session.get_if_active(session_id)
    if session and session.user.hosts_game(game):
        game.delete()
        return json.dumps({'success' : True})
    return json.dumps({'success' : False})

@client.route('/account/ship/add')
@json_status
def ship_add():
    return None #session_id
