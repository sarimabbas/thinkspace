import os
import re
import sys
import json
import helpers

from config import Config                       # config variables
from flask import Flask, g, request, jsonify    # flask web framework
from flask_httpauth import HTTPBasicAuth        # flask extension for authentication

# database models
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_migrate import Migrate

# parse requests (looks inside query, form and JSON data)
from datetime import date
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args

# CONNECTIONS
app = Flask(__name__)           # Flask
app.config.from_object(Config)  # config
auth = HTTPBasicAuth()          # Flask-HTTPauth
db = SQLAlchemy(app)            # Flask-SQLAlchemy
migrate = Migrate(app, db)      # Flask-Migrate

import models                   # import the database models (circular import)
import schemas

### client
@app.route("/")
def index():
    return "Hello world!"

## API v1

api_base = app.config["API_BASE"]

#### USERS

###### get users

######## validators

def userIdDoesNotExist(val):
    user = models.User.query.get(val)
    if user is None:
        raise ValidationError(
            "No user exists with this id.")

def usernameDoesNotExist(val):
    user = models.User.query.filter_by(username=val).first()
    if user is None:
        raise ValidationError(
            "No user exists with this username.")


def emailDoesNotExist(val):
    user = models.User.query.filter_by(email=val).first()
    if user is None:
        raise ValidationError(
            "No user exists with this email address.")

######## arguments

get_users_args = {
    "page" : fields.Int(required=False, missing="1"),
    "per_page" : fields.Int(required=False, missing="2"),
    "id": fields.Int(required=False, validate=userIdDoesNotExist),
    "username": fields.Str(required=False, validate=usernameDoesNotExist),
    "email": fields.Str(required=False, validate=[validate.Email(), emailDoesNotExist])
}

######## endpoint

@app.route(api_base + "/users", methods=["GET"])
@use_args(get_users_args)
def getUsers(args):
    schema = schemas.User(exclude=["password"])
    # get specific user
    if any(key in ["id", "username", "password"] for key in args.keys()):
        if "id" in args.keys():
            query = models.User.get(args["id"])
        elif "username" in args.keys():
            query = models.User.query.filter_by(username=args["username"]).first()
        elif "email" in args.keys():
            query = models.User.query.filter_by(email=args["email"]).first()
        result = schema.dump(query)
        return jsonify(result.data)
    # get multiple users
    else:
        query = models.User.query.paginate(args["page"], args["per_page"], False)
        items = query.items
        result = schema.dump(items, many=True)
        return jsonify(result.data)

###### create new user

######## validator methods

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

######## arguments

create_user_args = {
    "password": fields.Str(required=True, validate=validate.Length(min=6)),
    "username": fields.Str(required=True, validate=usernameExists),
    "email": fields.Str(required=True, validate=[validate.Email(), emailExists]),
    "first_name": fields.Str(required=False),
    "last_name" : fields.Str(required=False)
}

######## endpoint

@app.route(api_base + "/users", methods=["POST"])
@use_args(create_user_args)
def createUser(args):
    user = models.User()            # create new user
    for k, v in args.items():       # update its attributes
        if k == "password":
            setattr(user, k, helpers.hash(v))
        else:
            setattr(user, k, v)
    db.session.add(user)            # add to database
    db.session.commit()
    schema = schemas.User()         # dump and return
    result = schema.dump(user)
    return jsonify(result.data)

#### USER

###### get user

######## endpoint

@app.route(api_base + "/users/<int:id>", methods=["GET"])
def getUser(id):
    try:
        userIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422

    query = models.User.query.get(id)
    schema = schemas.User(exclude=["password"])
    result = schema.dump(query)
    return jsonify(result.data)

###### update user

######## helper functions

def hasSitePrivileges(username):
    user = models.User.query.filter_by(username=username).first()
    if user.site_admin or user.api_write:
        return True
    else:
        return False

######## arguments

update_user_args = {
    "first_name": fields.Str(required=False),
    "last_name": fields.Str(required=False),
    "email": fields.Str(required=False, validate=[validate.Email(), emailExists]),
    "site_admin": fields.Boolean(required=False),
    "site_curator": fields.Boolean(required=False),
    "api_write": fields.Boolean(required=False)
}

######## endpoint

@app.route(api_base + "/users/<int:id>", methods=["PUT"])
@auth.login_required
@use_args(update_user_args)
def updateUser(args, id):
    # check if user exists
    try:
        userIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422
    # updating protected properties requires site privileges
    if any(key in ["site_admin", "site_curator", "api_write"] for key in args.keys()):
        if not hasSitePrivileges(auth.username()):
            messages = ["You do not have permission to modify this user's protected properties."]
            return jsonify({'errors': {"auth": messages}}), 422
    # updating other properties requires the requestor to be the same user
    user = models.User.query.get(id)
    if(auth.username() != user.username):
        messages = ["You do not have permission to modify this user's basic properties."]
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

#### PROJECTS

###### get projects

######## validators

def projectIdDoesNotExist(val):
    project = models.Project.query.get(val)
    if project is None:
        raise ValidationError(
            "No project exists with this id.")

######## arguments

get_projects_args = {
    "page": fields.Int(required=False, missing="1"),
    "per_page": fields.Int(required=False, missing="2"),
    "id": fields.Int(required=False, validate=projectIdDoesNotExist),
}

######## endpoint

@app.route(api_base + "/projects", methods=["GET"])
@use_args(get_projects_args)
def getProjects(args):
    schema = schemas.Project()
    # get specific project
    if any(key in ["id"] for key in args.keys()):
        if "id" in args.keys():
            query = models.Project.query.get(args["id"])
        result = schema.dump(query)
        return jsonify(result.data)
    # get multiple projects
    else:
        query = models.Project.query.paginate(
            args["page"], args["per_page"], False)
        items = query.items
        result = schema.dump(items, many=True)
        return jsonify(result.data)

###### create new project

######## validator methods

def tagDoesNotExist(val):
    tags = models.Tag.query.all()
    tag_strs = []
    for tag in tags:
        tag_strs.append(tag.text)
    for key in val:
        if key not in tag_strs: 
            raise ValidationError(
                "One or more of your chosen tags do not exist.")

######## arguments

create_project_args = {
    "title": fields.Str(required=True),
    "subtitle": fields.Str(required=False),
    "description": fields.Str(required=False),
    "tags": fields.List(fields.Str(), required=False, validate=tagDoesNotExist)
}

######## endpoint

@app.route(api_base + "/projects", methods=["POST"])
@auth.login_required
@use_args(create_project_args)
def createProject(args):
    # create new project and update its basic attributes (not tags)
    project = models.Project()
    for k, v in args.items():
        if k != "tags":
            setattr(project, k, v)
    # update the project's tags separately
    if "tags" in args:
        for tag in args["tags"]:
            query = models.Tag.query.filter_by(text=tag).first()
            project.tags.append(query)
    # update the project's members and admin with the creating user
    user = models.User.query.filter_by(username=auth.username()).first()
    project.admin.append(user)
    project.members.append(user)
    # add to database
    db.session.add(project)            
    db.session.commit()
    # dump and return
    schema = schemas.Project()         
    result = schema.dump(project)
    return jsonify(result.data)

###### get project

######## endpoint

@app.route(api_base + "/projects/<int:id>", methods=["GET"])
def getProject(id):
    try:
        projectIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422

    query = models.Project.query.get(id)
    schema = schemas.Project()
    result = schema.dump(query)
    return jsonify(result.data)

###### update project

######## validators

def manyUsernamesDoNotExist(vals):
    for val in vals:
        user = models.User.query.filter_by(username=val).first()
        if user is None:
            raise ValidationError(
                "One or more users with the given usernames do not exist.")

######## helper functions

def hasProjectPrivileges(username, project_id):
    user = models.User.query.filter_by(username=username).first()
    project = models.Project.query.options(joinedload('admin')).get(project_id)
    if user in project.admin:
        return True
    else:
        return False

######## arguments

update_project_args = {
    "title": fields.Str(required=False),
    "subtitle": fields.Str(required=False),
    "description": fields.Str(required=False),
    "tags": fields.List(fields.Str(), required=False, validate=tagDoesNotExist),
    "members": fields.List(fields.Str(), required=False, validate=manyUsernamesDoNotExist),
    "admin": fields.List(fields.Str(), required=False, validate=manyUsernamesDoNotExist)
}

######## endpoint

@app.route(api_base + "/projects/<int:id>", methods=["PUT"])
@auth.login_required
@use_args(update_project_args)
def updateProject(args, id):
    # check if project exists
    try:
        projectIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422
    # check if requestor has project edit privileges
    if not hasProjectPrivileges(auth.username(), id) and not hasSitePrivileges(auth.username()):
        messages = ["You do not have permission to modify this project."]
        return jsonify({'errors': {"auth": messages}}), 422
    # update the project's basic properties
    project = models.Project.query.get(id)
    for k, v in args.items():
        if k not in ["tags", "admin", "members"]:
            setattr(project, k, v)
    # update the project's tags separately
    if "tags" in args:
        for tag in args["tags"]:
            query = models.Tag.query.filter_by(text=tag).first()
            project.tags.append(query)
    # update the project's admin separately
    if "admin" in args:
        for key in args["admin"]:
            query = models.User.query.filter_by(username=key).first()
            project.admin.append(query)
    # update the project's members separately
    if "members" in args:
        for key in args["members"]:
            query = models.User.query.filter_by(username=key).first()
            project.members.append(query)
    # commit to database
    db.session.commit()
    # dump and return
    schema = schemas.Project()
    result = schema.dump(project)
    return jsonify(result.data)

############## Convenience methods

heart_args = {
    "heartee" : fields.Str(required=True, validate=usernameDoesNotExist)
}
@app.route(api_base + "/users/heart", methods=["POST"])
@auth.login_required
@use_args(heart_args)
def heartUser(args):
    # get relevant users
    hearter = models.User.query.filter_by(username=auth.username()).first()
    heartee = models.User.query.filter_by(username=args["heartee"]).first()
    # check if already hearted
    if hearter in heartee.hearters:
        messages = ["You have already hearted this user."]
        return jsonify({'errors': {"heartee": messages}}), 422
    # heart
    heartee.hearters.append(hearter)
    heartee.hearts += 1
    # commit to database
    db.session.commit()
    # return both users
    schema = schemas.User(only=["hearts", "username", "hearters", "heartees"])
    result = schema.dump([hearter, heartee], many=True)
    return jsonify(result.data)

@app.route(api_base + "/users/unheart", methods=["POST"])
@auth.login_required
@use_args(heart_args)
def unheartUser(args):
    # get relevant users
    hearter = models.User.query.options(joinedload(
        'heartees')).filter_by(username=auth.username()).first()
    heartee = models.User.query.options(joinedload(
        'hearters')).filter_by(username=args["heartee"]).first()
    # check if already unhearted
    if hearter not in heartee.hearters:
        messages = ["You have already unhearted this user."]
        return jsonify({'errors': {"heartee": messages}}), 422
    # unheart
    heartee.hearters.remove(hearter)
    heartee.hearts -= 1
    # commit to database
    db.session.commit()
    # return both users
    schema = schemas.User(only=["hearts", "username", "hearters", "heartees"])
    result = schema.dump([hearter, heartee], many=True)
    return jsonify(result.data)

@auth.verify_password
def verify_password(username, password):
    """
    Uses HTTP Basic Auth (switch to JWT down the road)
    """
    g.username = None
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        return False
    if helpers.verify(password, user.password):
        g.username = username
        return True
    else:
        return False

@app.errorhandler(422)
def handle_validation_error(err):
    exc = err.exc
    return jsonify({'errors': exc.messages}), 422

@auth.error_handler
def handle_auth_error():
    messages = ["You were not successfully authenticated."]
    return jsonify({'errors': {"auth": messages}}), 401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True) # turn off debug for production
