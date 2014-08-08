from transcendentserver.extensions import db
from transcendentserver.constants import SHIP

class Ship(db.Model):
    __tablename__ = SHIP.TABLENAME

    id            = db.Column(db.Integer, primary_key=True)
