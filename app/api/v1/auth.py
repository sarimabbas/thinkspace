import app.models as models
import app.schemas as schemas

from app import db, jwt
from app.api.helpers import *
from app.api import bp

from flask import jsonify
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args
from flask_jwt_extended import get_jwt_identity, create_access_token

auth_args = {
    "username": fields.Str(required=True, validate=usernameDoesNotExist),
    "password": fields.Str(required=True)
}

@bp.route("/auth", methods=["POST"])
@use_args(auth_args)
def authy(args):
    # find the username in the databse
    user = models.User.query.filter_by(username=args["username"]).first()
    # check if user exists
    if user is None:
        return jsonify(messages=["You were not successfully authenticated."]), 401
    # check if the password passes authentication
    if passwordVerify(args["password"], user.password):
        # create an identity token from the username
        access_token = create_access_token(identity=args["username"])
        # return access token
        return jsonify(access_token=access_token, username=user.username, id=user.id)
    else:
        return jsonify(messages=["You were not successfully authenticated."]), 401

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint

@jwt.expired_token_loader
def expiredToken():
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'messages': ['The token has expired']
    }), 401

@jwt.invalid_token_loader
def invalidToken(arg):
    # arg is the inbuilt message, but i'm not using it
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'messages': ['No token was supplied, or token is invalid.']
    }), 401

@jwt.unauthorized_loader
def unauthorizedToken(arg):
    # arg is the inbuilt message, but i'm not using it
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'messages': ['You were not successfully authenticated.']
    }), 401
