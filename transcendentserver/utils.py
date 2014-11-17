from transcendentserver.constants import USER

from datetime import datetime
from struct import pack
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer, BadSignature

import os
import pickle
import bcrypt

def hash_password(plain_password, salt=None):
    if isinstance(plain_password, unicode):
        plain_password = plain_password.encode('u8')
    if not salt:
        salt = bcrypt.gensalt(USER.BCRYPT_WORK_FACTOR)
    elif isinstance(salt, unicode):
        salt = salt.encode('u8')
    return bcrypt.hashpw(plain_password, salt)

def get_current_datetime(*args, **kwargs):
    '''Returns a datetime object of the current datetime (UTC).
    Will ignore any arguments or keyword arguments'''
    return datetime.utcnow()

def get_validation_link(user_id):
    s = get_serializer()
    payload = s.dumps(str(user_id))
    return url_for('account.validate_email',
            payload=payload, _external=True)

def get_serializer(secret_key=None):
    '''Returns a signing serializer using a secret key, defaults to the app's'''
    if secret_key is None:
        secret_key = current_app.secret_key
    return URLSafeTimedSerializer(secret_key)

