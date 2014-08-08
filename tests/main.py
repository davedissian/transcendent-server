from flask.testing import FlaskClient
from transcendentserver import create_app

app = create_app()
tc = FlaskClient(app)

