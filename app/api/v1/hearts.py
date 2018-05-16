import app.models as models
import app.schemas as schemas

from app import db, jwt
from app.api.helpers import *
from app.api import bp

from flask import jsonify
from webargs import validate, fields, ValidationError
from webargs.flaskparser import parser, abort, use_args
from flask_jwt_extended import jwt_required, get_jwt_identity

heart_user_args = {
    "heart": fields.Boolean(required=True),
    "heartee": fields.Str(required=True, validate=usernameDoesNotExist)
}

@bp.route("/users/heart", methods=["POST"])
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
    schema = schemas.User(
        only=["id", "hearts", "username", "hearters", "heartees"])
    result_hearter = schema.dump(hearter)
    result_heartee = schema.dump(heartee)
    return jsonify({"hearter": result_hearter.data, "heartee": result_heartee.data})


heart_project_args = {
    "heart": fields.Boolean(required=True),
    "project": fields.Int(required=True, validate=projectIdDoesNotExist)
}


@bp.route("/projects/heart", methods=["POST"])
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
    schema_project = schemas.Project(
        only=["id", "title", "hearts", "hearters"])
    result_user = schema_user.dump(hearter)
    result_project = schema_project.dump(project)
    return jsonify({"user": result_user.data, "project": result_project.data})
