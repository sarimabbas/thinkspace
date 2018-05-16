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
from sqlalchemy.orm import joinedload

# authentication
from app import jwt

# parsing requests
from webargs import ValidationError

# other (security, permissions and validation)
from flask import jsonify
from passlib.apps import custom_app_context as pwd_context

############
# security #
############

def passwordHash(plaintext):
    return pwd_context.hash(plaintext)

def passwordVerify(plaintext, hashed):
    return pwd_context.verify(plaintext, hashed)

##################
# authentication #
##################

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

###############
# permissions #
###############

def hasSitePrivileges(username):
    user = models.User.query.filter_by(username=username).first()
    if user.site_admin or user.api_write:
        return True
    else:
        return False

def hasProjectPrivileges(username, project_id):
    user = models.User.query.filter_by(username=username).first()
    project = models.Project.query.options(joinedload('admin')).get(project_id)
    if user in project.admin:
        return True
    else:
        return False

##############
# validation #
##############

def userIdDoesNotExist(val):
    user = models.User.query.get(val)
    if user is None:
        raise ValidationError(
            "No user exists with this id.")

def projectIdDoesNotExist(val):
    project = models.Project.query.get(val)
    if project is None:
        raise ValidationError(
            "No project exists with this id.")

def usernameDoesNotExist(val):
    user = models.User.query.filter_by(username=val).first()
    if user is None:
        raise ValidationError(
            "No user exists with this username.")

def manyUsernamesDoNotExist(vals):
    for val in vals:
        user = models.User.query.filter_by(username=val).first()
        if user is None:
            raise ValidationError(
                "One or more users with the given usernames do not exist.")

def emailDoesNotExist(val):
    user = models.User.query.filter_by(email=val).first()
    if user is None:
        raise ValidationError(
            "No user exists with this email address.")

def tagDoesNotExist(val):
    tags = models.Tag.query.all()
    tag_strs = []
    for tag in tags:
        tag_strs.append(tag.text)
    for key in val:
        if key not in tag_strs:
            raise ValidationError(
                "One or more of your chosen tags do not exist.")

def usernameExists(val):
    user = models.User.query.filter_by(username=val).first()
    if user is not None:
        raise ValidationError(
            "A user already exists with this username.")

def emailExists(val):
    user = models.User.query.filter_by(email=val).first()
    if user is not None:
        raise ValidationError(
            "A user already exists with this email address.")

##########
# errors #
##########

@bp.errorhandler(422)
def handle_validation_error(err):
    exc = err.exc
    return jsonify({'errors': exc.messages}), 422
