# Also might be fit NoSQL well

from transcendentserver.extensions import db
from transcendentserver.constants import GAME, USER
from transcendentserver.utils import get_current_datetime

class Game(db.Model):
    __tablename__ = 'games'

    id           = db.Column(db.Integer, primary_key=True)
    host_guid    = db.Column(db.BigInteger, index=True)
    mode         = db.Column(db.SmallInteger, index=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('%s.id' % USER.TABLENAME))
    num_players  = db.Column(db.Integer, default=0) # TODO Foreign Key this to User
    max_players  = db.Column(db.Integer, default=GAME.MAX_PLAYERS_DEFAULT)
    created_at   = db.Column(db.DateTime, default=get_current_datetime)
    last_renewed = db.Column(db.DateTime, default=get_current_datetime)

    @classmethod
    def create_game(cls,host_guid, game_mode, user_id, max_players=None):
        new_game = Game(host_guid=host_guid, mode=game_mode, user_id=user_id, max_players=max_players)
        db.session.add(new_game)
        db.session.commit()
        return new_game

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def renew(self):
        self.last_renewed = get_current_datetime()

    @classmethod
    def delete_game(cls, guid):
        g = cls.get(guid)
        if g: 
            g.delete()

    @classmethod
    def get(cls, id):
        return cls.query.get(id)
