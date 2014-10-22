from transcendentserver.extensions import db, NPIDType
from transcendentserver.lib.npid import NPID
from transcendentserver.utils import get_current_datetime
from transcendentserver.constants import PURCHASE, USER, PRODUCT

class Purchase(db.Model):
    __tablename__ = PURCHASE.TABLENAME

    id            = db.Column(NPIDType, default=NPID, primary_key=True)
    user_id       = db.Column(NPIDType,
                              db.ForeignKey('%s.id' % USER.TABLENAME),
                              index=True, nullable=False)
    created_at    = db.Column(db.Datetime, default=get_current_datetime)
    product_id    = db.Column(NPIDType,
                              db.ForeignKey('%s.id' % PRODUCT.TABLENAME),
                              index=True, nullable=False)

    # Special properties set when the transaction is put through.
    # Should be completely immutable, not linked to the product_id.
    # This allows us to keep track of the price a person actually paid, even
    # across product name changes and price changes.
    purchase_price = db.Column(db.Decimal)
    product_name  = db.Column(db.String)
    

    @classmethod
    def purchases_by(cls, user):
        return cls.query.filter_by(user_id=user.id)

    @classmethod
    def has_purchased(cls, user, product):
        return cls.query.filter_by(user_id=user.id, product_id=product.id)

