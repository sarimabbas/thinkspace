import os
from datetime import timedelta

class Config(object):
    # databases
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"] 
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # flask
    DEBUG = True
    TESTING = True
    THREADED = True
    
    # json ordering of keys
    JSON_SORT_KEYS = False

    # API
    API_BASE = "/api/v1"
    
    # JWT tokens
    JWT_SECRET_KEY = "fancydonuts"
