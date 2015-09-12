# Could store some useful stuff in the session obj
# Location, IP Address - useful for matchmaking

from uuid import uuid4
from transcendentserver.utils import get_current_datetime
from transcendentserver.constants import SESSION, USER
from transcendentserver.extensions import db, UUIDType
# Later replace this with a Redis backend instead of the SQL backend.
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from base64 import urlsafe_b64encode
from transcendentserver.extensions import NPIDType
import os

def gen_session_id(*args, **kwargs):
    return urlsafe_b64encode(os.urandom(SESSION.KEY_LENGTH)).rstrip('=')

class Session(db.Model):
    __tablename__ = SESSION.TABLENAME

    id            = db.Column(db.String(SESSION.ID_LENGTH), default=gen_session_id, primary_key=True)
    user_id       = db.Column(NPIDType, db.ForeignKey('%s.id' % USER.TABLENAME), nullable=False)
    last_accessed = db.Column(db.DateTime, default=get_current_datetime)
    
    def authenticate_user_id(self, user_id):
        return self.user_id == user_id

    def authenticate_user(self, user):
        return self.user_id == user.id

    def authenticate_game(self, game):
        return self.user_id == game.user_id

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def authenticate_ids(cls, session_id, user_id):
        s = cls.get_if_active(session_id)
        return s and s.authenticate_user_id(user_id)

    @classmethod
    def create_session(cls, user):
        new_session = cls()
        new_session.user_id = user.id
        db.session.add(new_session)
        db.session.commit()
        return new_session

        
    @hybrid_property
    def expired(self):
        return get_current_datetime() > self.last_accessed + SESSION.LIFESPAN

    @expired.expression
    def expired(cls):
        return func.now() > cls.last_accessed + SESSION.LIFESPAN
        
    @classmethod
    def exists_and_active(cls, session_id):
        return get_if_active(session_id) != None

    @classmethod
    def get_if_active(cls, session_id):
        s = cls.get(session_id)
        if s and not s.expired:
            s.last_accessed = get_current_datetime()
            return s
        return None

    @classmethod
    def delete_expired_sessions(cls):
        cls.query.filter_by(expired=True).delete()

    @classmethod
    def delete_user_sessions(cls, user_id):
        '''Deletes all user sessions.'''
        cls.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
    def __repr__(self):
        return '<Session %r %r>' % (self.user_id, self.id)


