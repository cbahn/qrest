# import os

class Config(object):
    SECRET_KEY = "my very secret key"

    MONGO_DB_NAME = 'exampledb'

    COOKIE_NAME = 'qrest_session'
    ALLOW_SIGNUPS = False