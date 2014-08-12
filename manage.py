from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from transcendentserver import create_app
from transcendentserver.extensions import db

app = create_app()
manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def debug():
    app.config['DEBUG'] = True
    app.run()

@manager.command
def installdb():
    with app.test_request_context():
        db.drop_all()
        db.create_all()
        db.session.commit()

if __name__ == '__main__':
    manager.run()
