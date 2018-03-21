import os

class Config(object):
    # databases
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"] 
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MONGODB_URI = os.environ["MONGODB_URI"]

    # flask
    DEBUG = True
    TESTING = True
    
    # json ordering of keys
    JSON_SORT_KEYS = False

    # API
    API_BASE = "/api/v1"