from transcendentserver.extensions import db, NPIDType
from transcendentserver.lib.npid import NPID
from transcendentserver.constants import USER, PURCHASE
from transcendentserver.controls.steam import get_steam_userinfo
from transcendentserver.utils import hash_password, get_current_datetime
from flask_login import UserMixin
from transcendentserver.models import Purchase

from werkzeug.security import safe_str_cmp

class User(db.Model, UserMixin):
    __tablename__   = USER.TABLENAME
    
    id              = db.Column(NPIDType, default=NPID, primary_key=True)
    steam_id        = db.Column(db.BigInteger, index=True, unique=True)
    name            = db.Column(db.String(USER.MAX_NAME_LENGTH), index=True, unique=True)
    email           = db.Column(db.String(USER.MAX_EMAIL_LENGTH), index=True, unique=True)
    _password       = db.Column(db.String(USER.BCRYPT_HASH_LENGTH))
    role            = db.Column(db.SmallInteger, default=USER.ROLES.NEW)
    validated_email = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=get_current_datetime)

    current_session = db.relationship('Session', 
                                      backref=db.backref('user',
                                                         lazy='joined'), 
                                      lazy='joined')

    def get_password(self):
        return self._password.encode('utf-8')

    def set_password(self, plain_password):
        self._password = hash_password(plain_password)

    password = property(fget=get_password, fset=set_password)

    def check_password(self, plain_password):
        '''Validates the user's password
        Parameters:
            pain_password: The password to check in plain text
        Returns:
            Bool: True if the parameter matches the stored hash
        '''

        password_hash = hash_password(plain_password, self.password)
        return safe_str_cmp(password_hash, self.password)

    def validate_email(self):
        '''Marks the user's email as validated'''
        self.validated_email = True

    def hosts_lobby(self, lobby):
        '''Returns whether the user is hosting the provided game
        Parameters:
            lobby: The lobby to check against
        Returns:
            Bool: True if the current user is the lobby host
        '''
        return self.id == lobby.user_id

    def refresh_steam_name(self):
        if self.steam_id:
            steam_data = get_steam_userinfo(self.steam_id)
            self.name = steam_data['personaname']

    def can_play(self):
        purchases = Purchase.purchases_by(self).all()
        return PURCHASE.ITEM.EARLY_ALPHA in purchases

    @classmethod
    def register_new_user(cls, name, email, password):
        new_user = cls()
        new_user.name = name
        new_user.email = email
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def register_new_steam_user(cls, steam_id):
        new_user = cls()
        steam_data = get_steam_userinfo(steam_id)
        new_user.name = steam_data['personaname']
        new_user.email = None
        new_user.steam_id = steam_id
        db.session.add(new_user)
        db.session.commit()
        return new_user


    @classmethod
    def get(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def find(cls, name):
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return '<User %r>' % (self.name)
