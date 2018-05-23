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
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, desc, text

# authentication
from app import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity

# parsing requests
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args

# other (security, permissions and validation)
from flask import jsonify
from . import helpers

#############
# get users #
#############

# arguments
get_users_args = {
    # pagination
    "page": fields.Int(required=False, missing="1"),
    "per_page": fields.Int(required=False, missing="5"),
    # narrowing the results
    "search": fields.Str(required=False),
    "sort": fields.Str(required=False, 
                        validate=lambda val: val in ["hearts", "-hearts", "timestamp", "-timestamp"], 
                        missing="-timestamp")
}

# route
@bp.route("/users", methods=["GET"])
@use_args(get_users_args)
def getUsers(args):
    # search
    if "search" in args: # specific search
        query = models.User.query.filter(or_(
            models.User.username == args["search"], 
            models.User.email == args["search"], 
            models.User.first_name.ilike("%" + args["search"] + "%"),
            models.User.last_name.ilike("%" + args["search"] + "%")
        ))
    else: # broad search
        query = models.User.query
    # sorting
    if "sort" in args:
        if "-" in args["sort"]:
            order_arg = args["sort"].replace("-", "")
            query = query.order_by(desc(text(order_arg)))
        else:
            order_arg = args["sort"]
            query = query.order_by(text(order_arg))
    # pagination
    query = query.paginate(args["page"], args["per_page"], False)
    # return data
    items = []
    items = query.items
    if items:
        schema = schemas.User(exclude=["password"])
        result = schema.dump(items, many=True)
        return jsonify(result.data)
    else:
        return jsonify([])

###################
# create new user #
###################

# arguments
create_user_args = {
    "password": fields.Str(required=True, validate=validate.Length(min=6)),
    "username": fields.Str(required=True, validate=helpers.usernameExists),
    "email": fields.Str(required=True, validate=[validate.Email(), helpers.emailExists]),
    "first_name": fields.Str(required=False),
    "last_name": fields.Str(required=False)
}

# route
@bp.route("/users", methods=["POST"])
@use_args(create_user_args)
def createUser(args):
    user = models.User()            # create new user
    for k, v in args.items():       # update its attributes
        if k == "password":
            setattr(user, k, helpers.passwordHash(v))
        else:
            setattr(user, k, v)
    db.session.add(user)            # add to database
    db.session.commit()
    schema = schemas.User()         # dump and return
    result = schema.dump(user)
    return jsonify(result.data)

#####################
# get specific user #
#####################

# route
@bp.route("/users/<int:id>", methods=["GET"])
def getUser(id):
    try:
        helpers.userIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422

    query = models.User.query.get(id)
    schema = schemas.User(exclude=["password"])
    result = schema.dump(query)
    return jsonify(result.data)

########################
# update specific user #
########################

# arguments
update_user_args = {
    "first_name": fields.Str(required=False),
    "last_name": fields.Str(required=False),
    "email": fields.Str(required=False, validate=[validate.Email(), helpers.emailExists]),
    "site_admin": fields.Boolean(required=False),
    "site_curator": fields.Boolean(required=False),
    "api_write": fields.Boolean(required=False)
}

# routes
@bp.route("/users/<int:id>", methods=["PUT"])
@jwt_required
@use_args(update_user_args)
def updateUser(args, id):
    # check if user exists
    try:
        helpers.userIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422
    user = models.User.query.get(id)
    # updating protected properties requires site privileges
    if any(key in ["site_admin", "site_curator", "api_write"] for key in args.keys()):
        if not helpers.hasSitePrivileges(get_jwt_identity()):
            messages = [
                "You do not have permission to modify this user's protected properties."]
            return jsonify({'errors': {"auth": messages}}), 422
    # updating other properties requires the requestor to be the same user
    elif(get_jwt_identity() != user.username):
        messages = [
            "You do not have permission to modify this user's basic properties."]
        return jsonify({'errors': {"auth": messages}}), 422
    # update properties
    for k, v in args.items():
        setattr(user, k, v)
    # commit to database
    db.session.commit()
    # dump and return
    schema = schemas.User(exclude=["password"])
    result = schema.dump(user)
    return jsonify(result.data)

    
