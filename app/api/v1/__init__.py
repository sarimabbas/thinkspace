# extension to help create BluePrints
from flask import Blueprint

# create a blueprint for the many routes
bp = Blueprint('api_v1', __name__, url_prefix="/api/v1")

# import the different modules with their respective routes into __init__.py
# the . tells __init__.py to look in the current directory for these modules
from . import users
