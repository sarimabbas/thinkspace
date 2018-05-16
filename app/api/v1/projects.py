from app import db, jwt

import app.models as models
import app.schemas as schemas

from app.api.helpers import *
from app.api import bp

from flask import jsonify
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args
from flask_jwt_extended import jwt_required, get_jwt_identity

get_projects_args = {
    "page": fields.Int(required=False, missing="1"),
    "per_page": fields.Int(required=False, missing="2"),
    "id": fields.Int(required=False, validate=projectIdDoesNotExist),
}

@bp.route("/projects", methods=["GET"])
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

@bp.route("/projects", methods=["POST"])
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


@bp.route("/projects/<int:id>", methods=["GET"])
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


@bp.route("/projects/<int:id>", methods=["PUT"])
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
