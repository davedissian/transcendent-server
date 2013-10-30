from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_mail import Mail
mail = Mail()

from flask_assets import Environment, Bundle
assets = Environment()

from flask_cache import Cache
cache = Cache()

from sqlalchemy import types
import uuid

class UUIDType(types.TypeDecorator):
    impl = types.BINARY

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self,length=self.impl.length)

    def process_bind_param(self,value,dialect=None):
        if value and isinstance(value,uuid.UUID):
            return value.bytes
        elif value and not isinstance(value,uuid.UUID):
            raise ValueError,'value %s is not a valid uuid.UUID' % value
        else:
            return None

    def process_result_value(self,value,dialect=None):
        if value:
            return uuid.UUID(bytes=value)
        else:
            return None

    def is_mutable(self):
        return False

