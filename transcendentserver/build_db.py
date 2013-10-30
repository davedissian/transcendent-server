from . import create_app
from transcendentserver.extensions import db
from transcendentserver.models import *
app = create_app()
with app.test_request_context():
    db.drop_all()
    db.create_all()
    db.session.commit()
