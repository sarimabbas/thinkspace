import os
import sys
import timeago
import requests

from config import Config                                       # config variables
from flask import Flask, g, request, jsonify, render_template   # flask web framework
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

# database models
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_migrate import Migrate

# parse requests (looks inside query, form and JSON data)
from datetime import date, datetime
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args

# CONNECTIONS
app = Flask(__name__)                   # Flask
app.config.from_object(Config)          # config
db = SQLAlchemy(app)                    # Flask-SQLAlchemy
migrate = Migrate(app, db)              # Flask-Migrate
jwt = JWTManager(app)

import models                           # import the database models (circular import)
import schemas
from helpers import *

### client

client_base = "http://127.0.0.1:5000/api/v1"

def humanReadableTime(timestamp):
    if timestamp is None or "":
        old = datetime.now()
    else:
        old = datetime.strptime(timestamp[0:19], "%Y-%m-%dT%H:%M:%S")
    return timeago.format(old, datetime.now())

app.jinja_env.filters['humanReadableTime'] = humanReadableTime

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projects", methods=["GET"])
def projects():
    url = client_base + "/projects"
    payload = "{\n\t\"page\" : 1,\n\t\"per_page\" : 5\n}"
    headers = {'content-type': 'application/json'}
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    return render_template("projects.html", projects=data)

@app.route("/projects/<int:id>", methods=["GET"])
def project(id):
    url = client_base + "/projects/" + str(id)
    response = requests.request("GET", url)
    data = response.json()
    return render_template("project.html", project=data)

## API v1

api_base = app.config["API_BASE"]

#### USERS

###### get users
get_users_args = {
    "page" : fields.Int(required=False, missing="1"),
    "per_page" : fields.Int(required=False, missing="2"),
    "id": fields.Int(required=False, validate=userIdDoesNotExist),
    "username": fields.Str(required=False, validate=usernameDoesNotExist),
    "email": fields.Str(required=False, validate=[validate.Email(), emailDoesNotExist])
}
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
create_user_args = {
    "password": fields.Str(required=True, validate=validate.Length(min=6)),
    "username": fields.Str(required=True, validate=usernameExists),
    "email": fields.Str(required=True, validate=[validate.Email(), emailExists]),
    "first_name": fields.Str(required=False),
    "last_name" : fields.Str(required=False)
}
@app.route(api_base + "/users", methods=["POST"])
@use_args(create_user_args)
def createUser(args):
    user = models.User()            # create new user
    for k, v in args.items():       # update its attributes
        if k == "password":
            setattr(user, k, passwordHash(v))
        else:
            setattr(user, k, v)
    db.session.add(user)            # add to database
    db.session.commit()
    schema = schemas.User()         # dump and return
    result = schema.dump(user)
    return jsonify(result.data)

#### USER

###### get user
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
update_user_args = {
    "first_name": fields.Str(required=False),
    "last_name": fields.Str(required=False),
    "email": fields.Str(required=False, validate=[validate.Email(), emailExists]),
    "site_admin": fields.Boolean(required=False),
    "site_curator": fields.Boolean(required=False),
    "api_write": fields.Boolean(required=False)
}
@app.route(api_base + "/users/<int:id>", methods=["PUT"])
@jwt_required
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
        if not hasSitePrivileges(get_jwt_identity()):
            messages = ["You do not have permission to modify this user's protected properties."]
            return jsonify({'errors': {"auth": messages}}), 422
    # updating other properties requires the requestor to be the same user
    user = models.User.query.get(id)
    if(get_jwt_identity() != user.username):
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
get_projects_args = {
    "page": fields.Int(required=False, missing="1"),
    "per_page": fields.Int(required=False, missing="2"),
    "id": fields.Int(required=False, validate=projectIdDoesNotExist),
}
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
create_project_args = {
    "title": fields.Str(required=True),
    "subtitle": fields.Str(required=False),
    "description": fields.Str(required=False),
    "tags": fields.List(fields.Str(), required=False, validate=tagDoesNotExist)
}
@app.route(api_base + "/projects", methods=["POST"])
@jwt_required
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
    user = models.User.query.filter_by(username=get_jwt_identity()).first()
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
update_project_args = {
    "title": fields.Str(required=False),
    "subtitle": fields.Str(required=False),
    "description": fields.Str(required=False),
    "tags": fields.List(fields.Str(), required=False, validate=tagDoesNotExist),
    "members": fields.List(fields.Str(), required=False, validate=manyUsernamesDoNotExist),
    "admin": fields.List(fields.Str(), required=False, validate=manyUsernamesDoNotExist)
}
@app.route(api_base + "/projects/<int:id>", methods=["PUT"])
@jwt_required
@use_args(update_project_args)
def updateProject(args, id):
    # check if project exists
    try:
        projectIdDoesNotExist(id)
    except ValidationError as e:
        messages = e.messages
        return jsonify({'errors': {"id": messages}}), 422
    # check if requestor has project edit privileges
    if not hasProjectPrivileges(get_jwt_identity(), id) and not hasSitePrivileges(get_jwt_identity()):
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

heart_user_args = {
    "heart" : fields.Boolean(required=True),
    "heartee" : fields.Str(required=True, validate=usernameDoesNotExist)
}
@app.route(api_base + "/users/heart", methods=["POST"])
@jwt_required
@use_args(heart_user_args)
def heartUser(args):
    # get relevant users
    hearter = models.User.query.filter_by(username=get_jwt_identity()).first()
    heartee = models.User.query.filter_by(username=args["heartee"]).first()
    if args["heart"] == True:
        # check if already hearted
        if hearter in heartee.hearters:
            messages = ["You have already hearted this user."]
            return jsonify({'errors': {"heartee": messages}}), 422
        # heart
        heartee.hearters.append(hearter)
        heartee.hearts += 1
    else:
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
    schema = schemas.User(only=["id", "hearts", "username", "hearters", "heartees"])
    result_hearter = schema.dump(hearter)
    result_heartee = schema.dump(heartee)
    return jsonify({"hearter" : result_hearter.data, "heartee" : result_heartee.data})


heart_project_args = {
    "heart": fields.Boolean(required=True),
    "project": fields.Int(required=True, validate=projectIdDoesNotExist)
}

@app.route(api_base + "/projects/heart", methods=["POST"])
@jwt_required
@use_args(heart_project_args)
def heartProject(args):
    # get relevant user and project
    hearter = models.User.query.filter_by(username=get_jwt_identity()).first()
    project = models.Project.query.get(args["project"])
    if args["heart"] == True:
        # check if already hearted
        if hearter in project.hearters:
            messages = ["You have already hearted this project."]
            return jsonify({'errors': {"project": messages}}), 422
        # heart
        project.hearters.append(hearter)
        project.hearts += 1
    else:
        # check if already unhearted
        if hearter not in project.hearters:
            messages = ["You have already unhearted this project."]
            return jsonify({'errors': {"project": messages}}), 422
        # unheart
        project.hearters.remove(hearter)
        project.hearts -= 1
    # commit to database
    db.session.commit()
    # return both users
    schema_user = schemas.User(only=["id", "username", "hearted_projects"])
    schema_project = schemas.Project(only=["id", "title", "hearts", "hearters"])
    result_user = schema_user.dump(hearter)
    result_project = schema_project.dump(project)
    return jsonify({"user" : result_user.data, "project" : result_project.data})

###### create new comment
create_comment_args = {
    "content": fields.Str(required=True),
    "project" : fields.Int(required=True, validate=projectIdDoesNotExist)
}

@app.route(api_base + "/comments", methods=["POST"])
@jwt_required
@use_args(create_comment_args)
def createComment(args):
    # get the project and the user
    project = models.Project.query.get(args["project"])
    user = models.User.query.filter_by(username=get_jwt_identity()).first()
    # create a comment
    comment = models.Comment(content=args["content"], user_id=user.id, project_id=project.id)
    # add to database
    db.session.add(comment)
    db.session.commit()
    # dump and return
    schema_comment = schemas.Comment()
    result = schema_comment.dump(comment)
    return jsonify(result.data)

#### authentication and error handling

auth_args = {
    "username" : fields.Str(required=True, validate=usernameDoesNotExist),
    "password" : fields.Str(required=True)
}

@app.route(api_base + "/auth", methods=["POST"])
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

@app.errorhandler(422)
def handle_validation_error(err):
    exc = err.exc
    return jsonify({'errors': exc.messages}), 422

if __name__ == "__main__":
    app.run(threaded=True)
