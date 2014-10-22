from transcendentserver.constants import PRODUCT
from transcendentserver.extensions import db, NPIDType
from transcendentserver.lib.npid import NPID
from transcendentserver.utils import get_current_datetime

class Product(db.Model):
    __tablename__ = PRODUCT.TABLENAME

    id            = db.Column(NPIDType, default=NPID, primary_key=True)
    name          = db.Column(db.String)
