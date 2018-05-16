# extension to help create BluePrints
from flask import Blueprint

# create a blueprint for the many routes
bp = Blueprint('api_v1', __name__, url_prefix="/api/v1")

# import modules containing routes into __init__.py
# the . tells __init__.py to look in the current directory for these modules
from . import users, projects, hearts, auth, helpers
