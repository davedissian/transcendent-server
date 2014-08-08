from datetime import timedelta
FIFTEEN_MINS = timedelta(0, 15 * 60, 0)
HALF_DAY = timedelta(0.5)
DAY = timedelta(1)
WEEK = timedelta(7)

class SESSION:
    TABLENAME  = 'sessions'
    LIFESPAN   = HALF_DAY
    KEY_LENGTH = 16
    ID_LENGTH  = 22

class USER:
    TABLENAME           = 'users'
    MAX_NAME_LENGTH     = 30
    BCRYPT_WORK_FACTOR  = 12
    MAX_EMAIL_LENGTH    = 120
    BCRYPT_HASH_LENGTH  = 60
    MIN_PASSWORD_LENGTH = 10
    VALIDATION_URL_LIFETIME = int(DAY.total_seconds())
    class ROLES:
        ADMIN    = 0
        STANDARD = 1
        NEW      = 2

class LOBBY:
    TABLENAME           = 'lobbies'
    MAX_PLAYERS_DEFAULT = 16

class HTTP:
    OK           = 200
    CREATED      = 201

    UNAUTHORIZED = 401
    NOTFOUND     = 404

class MAIL:
    ROBOT   = 'donotreply@transcendent.local'
    WORKERS = 1

    class PRIORITY:
        URGENT            = 0
        PASSWORD_RECOVERY = 1
        NORMAL            = 2
        VALIDATION        = 3

class MATCHMAKING:
    LOBBY_LIST_LIMIT = 30

class SHIP:
    TABLENAME = 'ships'
