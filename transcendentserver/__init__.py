from flask import Flask
from transcendentserver.extensions import db, login_manager, mail, assets, cache
from transcendentserver.views import account, base, client
from wtforms.fields import HiddenField
from transcendentserver.controls import mailer
from transcendentserver.models import User
from transcendentserver.constants import MAIL
from transcendentserver.lib.npid import NPID

import os
import sys

def create_app():
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)
    configure_filters(app)
    configure_extensions(app)
    configure_blueprints(app)
    configure_async_mailer(app)
    return app

def configure_async_mailer(app):
    mailer.setup_workers()

def configure_filters(app):
    def bootstrap_is_hidden_field_filter(field):
        return isinstance(field, HiddenField)
    app.jinja_env.globals['bootstrap_is_hidden_field'] = bootstrap_is_hidden_field_filter

def configure_blueprints(app):
    app.register_blueprint(base, url_prefix='/')
    app.register_blueprint(client, url_prefix='/client')
    app.register_blueprint(account, url_prefix='/account')

class DefaultConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/transcendentserver.db'
    DEBUG = True
    SECRET_KEY = '\xe3\xfd\xdb\xb6A\xda"\xeb@NA\xf7\xa2\x0ccs\x13\x8b\x85\xec\xcb\x11\xe7$M\x11\x7f\x986a\xab]'
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_USERNAME = 'nicprettejohn@gmail.com'
    MAIL_PASSWORD = 'pkjdvniwmsstmpsp'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    DEFAULT_MAIL_SENDER = MAIL.ROBOT
    CACHE_TYPE = 'simple'
    STEAM_API_KEY = ''

def configure_extensions(app):
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    assets.init_app(app)
    cache.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        if not isinstance(userid, NPID):
            userid = NPID(hex=userid)
        return User.get(userid)

