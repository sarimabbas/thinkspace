###########
# imports #
###########

# blueprint for routing
from app.api.v1 import bp

# database models and schemas
from app import db
import app.models
from app.models import models
from app.models import schemas

# authentication
from app import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

# parsing requests
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args

# other (security, permissions and validation)
from flask import jsonify
from . import helpers

##################
# return a token #
##################

auth_args = {
    "username": fields.Str(required=True, validate=helpers.usernameDoesNotExist),
    "password": fields.Str(required=True)
}

@bp.route("/auth", methods=["GET"])
@use_args(auth_args)
def auth(args):
    # find the username in the databse
    user = models.User.query.filter_by(username=args["username"]).first()
    # check if user exists
    if user is None:
        return jsonify(errors=["Incorrect username or password."]), 401
    # check if the password passes authentication
    if helpers.passwordVerify(args["password"], user.password):
        # create an identity token from the username
        access_token = create_access_token(identity=args["username"])
        # return access token
        return jsonify(access_token=access_token, username=user.username, id=user.id)
    else:
        return jsonify(errors=["Incorrect username or password."]), 401

@bp.route("/whoami", methods=["GET"])
@jwt_required
def whoami():
    user = models.User.query.filter_by(username=get_jwt_identity()).first()
    schema = schemas.User(exclude=["password"])
    result = schema.dump(user)
    return jsonify(result.data)
