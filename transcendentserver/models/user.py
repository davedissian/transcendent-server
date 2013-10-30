from transcendentserver.extensions import db
from transcendentserver.constants import USER
from transcendentserver.utils import hash_password, get_current_datetime
from flask_login import UserMixin

from werkzeug.security import safe_str_cmp

class User(db.Model, UserMixin):
    __tablename__   = USER.TABLENAME

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(USER.MAX_NAME_LENGTH), index=True, unique=True)
    email           = db.Column(db.String(USER.MAX_EMAIL_LENGTH), unique=True)
    _password       = db.Column(db.String(USER.BCRYPT_HASH_LENGTH))
    role            = db.Column(db.SmallInteger, default=USER.ROLES.NEW)
    validated_email = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=get_current_datetime)

    current_session = db.relationship('Session', 
                        backref=db.backref('user',lazy='joined'), 
                        lazy='joined')


    def get_password(self):
        return self._password

    def set_password(self, plain_password):
        self._password = hash_password(plain_password)

    password = property(fget=get_password, fset=set_password)

    def check_password(self, plain_password):
        password_hash = hash_password(plain_password, self.password)
        return safe_str_cmp(password_hash, self.password)

    def validate_email(self):
        '''Marks the user's email as validated'''
        self.validated_email = True

    def hosts_game(self, game):
        return self.id == game.user_id

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
    def get(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def find(cls, name):
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return '<User %r>' % (self.name)
