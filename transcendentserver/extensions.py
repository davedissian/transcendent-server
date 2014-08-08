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

from flask_restful import Api
api = Api()

from sqlalchemy import types

from transcendentserver.lib.npid import NPID

class NPIDType(types.TypeDecorator):
    impl = types.CHAR
    
    def __init__(self):
        self.impl.length = 32
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, NPID):
            return value.hex()
        elif value and not isinstance(value, NPID):
            return ValueError, 'Value {0} is not a valid NPID'.format(
                                                                  repr(value))
        else:
            return None
    
    def process_result_value(self,value,dialect=None):
        if value:
            return NPID(hex=value)
        else:
            return None

    #def coerce_compared_value(self, op, value):
    #    print 'Coerce compared value', value
    #    if isinstance(value, NPID):
    #        return value.hex()
    #    return value

    def is_mutable(self):
        return False

class UUIDType(types.TypeDecorator):
    impl = types.BINARY

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self,length=self.impl.length)

    def process_bind_param(self,value,dialect=None):
        if value and isinstance(value, uuid.UUID):
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

