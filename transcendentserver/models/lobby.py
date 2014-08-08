from transcendentserver.extensions import db
from transcendentserver.constants import LOBBY, USER
from transcendentserver.utils import get_current_datetime
from transcendentserver.extensions import NPIDType
from transcendentserver.lib.npid import NPID

class Lobby(db.Model):
    __tablename__ = LOBBY.TABLENAME

    id           = db.Column(NPIDType, default=NPID, primary_key=True)
    host_guid    = db.Column(db.BigInteger, index=True)
    mode         = db.Column(db.SmallInteger, index=True)
    host_user_id = db.Column(NPIDType, db.ForeignKey('%s.id' % USER.TABLENAME))
    num_players  = db.Column(db.Integer, default=0, index=True) # TODO Foreign Key this to User
    max_players  = db.Column(db.Integer, default=LOBBY.MAX_PLAYERS_DEFAULT)
    created_at   = db.Column(db.DateTime, default=get_current_datetime)
    last_renewed = db.Column(db.DateTime, default=get_current_datetime)

    @classmethod
    def create_lobby(cls, host_guid, game_mode, host_user_id, max_players=None):
        new_lobby = Lobby(host_guid=host_guid, mode=game_mode, host_user_id=host_user_id, max_players=max_players)
        db.session.add(new_lobby)
        db.session.commit()
        return new_lobby

    def delete(self):
        '''
            Deletes the lobby, does any clean up, and removes the record from
            the databfase
        '''
        db.session.delete(self)
        db.session.commit()

    def renew(self):
        self.last_renewed = get_current_datetime()
        db.session.commit()

    @classmethod
    def delete_lobby(cls, guid):
        g = cls.get(guid)
        if g: 
            g.delete()

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    def change_host(self, user, guid):
        self.host_user_id = user.id
        self.host_guid = guid
        db.session.commit()
    
