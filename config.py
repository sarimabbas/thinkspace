import os
from datetime import timedelta

class developmentConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"] 
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_SECRET_KEY = os.urandom(24)


class productionConfig(object):
    THREADED = True
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    JWT_SECRET_KEY = os.urandom(24)
