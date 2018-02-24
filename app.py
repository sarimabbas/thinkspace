import os
import re
import sys
import json

# helper functions
import helpers
# models for storing data in mongodb (may consider postgres later)
import models
# flask web framework
from flask import Flask, g, request
# flask extension for easy API endpoint creation
from flask_restful import Api, Resource
# flask extension for authentication
from flask_httpauth import HTTPBasicAuth

# ODM for mongodb
from mongoengine import *

# parse requests (looks inside query, form and JSON data)
from datetime import date
from webargs import validate
from webargs.flaskparser import parser, abort
from marshmallow import Schema, fields, pprint

# handle exceptions
from contextlib import contextmanager

# connections
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.config["DATABASE_URI"] = os.environ.get("MONGODB_URI")
db = connect(db="thinkspace", host=app.config["DATABASE_URI"])

### client
@app.route("/")
def index():
    return "Hello world!"

### API
class Projects(Resource):
    def get(self):
        """
        Gets a list of projects in the database
        Access: public
        """
        query_set = models.Project.objects()
        return helpers.mongo2json(query_set), 200 # OK

    @auth.login_required
    def post(self):
        """
        Creates a new project in the database,
        and registers the requester as a user and founder
        Access: logged in users
        """
        webargs = request.json
        project = models.Project()
        if docUpsert(project, webargs):
            # register the requester
            user = models.User.objects.get(username = g.username)
            project.users.append(user)
            project.project_roles = models.ProjectRoles()
            project.project_roles.founders.append(user)
            if attemptSave(project):
                return helpers.mongo2json(project), 201 # Created

class Project(Resource):
    def get(self, doc_id):
        """
        Gets a project in the database
        doc_id: the object id of the document instance
        Access: public
        """
        # validate id
        if not helpers.isValidId(doc_id):
            abort(400)

        # search for project
        query_set = models.Project.objects(id=doc_id)
        if query_set:
            project = query_set[0]
            return helpers.mongo2json(project), 200 # OK
        else:
            abort(404) # Not Found

    @auth.login_required
    def put(self, doc_id):
        """
        Updates or adds a project in the database (for new projects, send POST to /projects instead)
        doc_id: the object id of the document instance
        Access: site curators, site admin, project leaders, project founders
        """
        # validate id
        if not helpers.isValidId(doc_id):
            abort(400) # Bad Request

        # check permissions / roles
        if not (
        checkSiteRole(g.username, "curator") or
        checkSiteRole(g.username, "admin") or
        checkProjectRole(g.username, doc_id, "leaders") or
        checkProjectRole(g.username, doc_id, "founders")
        ):
            abort(403) # forbidden

        # update or create project
        webargs = request.json
        query_set = models.Project.objects(id=doc_id)
        if query_set: # i.e if the project exists
            project = query_set[0]
            if docUpsert(project, webargs):
                return helpers.mongo2json(project), 200 # OK
        else:
            project = models.Project()
            project.project_roles = models.ProjectRoles()
            if docUpsert(project, webargs):
                return helpers.mongo2json(project), 201 # Created

    @auth.login_required
    def delete(self, doc_id):
        """
        Deletes a project from the database
        doc_id: the object id of the document instance
        Access: site curators, site admin, project leaders, project founders
        """
        # validate id
        if not helpers.isValidId(doc_id):
            abort(400) # Bad Request

        # get project
        query_set = models.Project.objects(id=doc_id)
        if query_set:
            project = query_set[0]
        else:
            abort(404) # not found

        # check permissions / roles
        if not (
        checkSiteRole(g.username, "curator") or
        checkSiteRole(g.username, "admin") or
        checkProjectRole(g.username, doc_id, "leaders") or
        checkProjectRole(g.username, doc_id, "founders")
        ):
            abort(403) # Forbidden

        # delete project
        project.delete()
        return "", 204 # No Content

class Users(Resource):
    def get(self):
        """
        Gets a list of users in the database
        Access: public
        Optional request params:
            username
            email
        """
        query_set = models.User.objects().exclude("password")
        return helpers.mongo2json(query_set)

    def post(self):
        """
        Creates a new user in the database
        Access: public
        """
        webargs = request.json
        user = models.User()
        user.site_roles = models.SiteRoles()
        user.links = models.Links()
        if docUpsert(user, webargs):
            return helpers.mongo2json(user), 201 # Created

class User(Resource):
    def get(self, doc_id):
        """
        Gets a user in the database
        doc_id: the object id of the document instance
        Access: public
        """
        # validate id
        if not helpers.isValidId(doc_id):
            abort(400) # Bad Request

        # search for user
        query_set = models.User.objects(id=doc_id).exclude("password")
        if query_set:
            user = query_set[0]
            return helpers.mongo2json(user), 200 # OK
        else:
            abort(404) # Not Found

    @auth.login_required
    def put(self, doc_id):
        """
        Updates or adds a user in the database (for new users, send POST to /users instead)
        doc_id: the object id of the document instance
        Access: the user itself, site admin
        """
        # validate id
        if not helpers.isValidId(doc_id):
            abort(400) # Bad Request

        # update or create user
        webargs = request.json
        query_set = models.User.objects(id=doc_id)
        if query_set: # if the user exists
            user = query_set[0]
            # check permissions / roles for the logged in user
            if not (
            checkSiteRole(g.username, "admin") or
            g.username == user.username
            ):
                abort(403) # forbidden
            # update the user
            if docUpsert(user, webargs):
                return helpers.mongo2json(user), 200 # OK
        else: # if the user does not exist
            user = models.User()
            user.site_roles = models.SiteRoles()
            user.links = models.Links()
            if docUpsert(user, webargs):
                return helpers.mongo2json(user), 201 # Created

    @auth.login_required
    def delete(self, doc_id):
        """
        Deletes a user from the database
        doc_id: the object id of the document instance
        Access: the user itself, site admin
        """
        # validate id
        if not helpers.isValidId(doc_id):
            abort(400) # bad request

        # get user
        query_set = models.User.objects(id=doc_id)
        if query_set:
            user = query_set[0]
        else:
            abort(404) # not found

        # check permissions
        if not (
        checkSiteRole(g.username, "admin") or
        g. username == user.username
        ):
            abort(403) # forbidden

        # delete user
        user.delete()
        return "", 204

def docUpsert(doc, args):
    """
    Inserts or updates a document with given arguments, then attempts a save
    document:   a model instance from the database
    args:       arguments (usually from request)
    """
    for key in args:
        if key in doc._fields and args[key]:
            if key == "password":
                doc[key] = helpers.hash(args[key])
            elif type(args[key]) == type({}):
                docUpsert(doc[key], args[key])
            else:
                doc[key] = args[key]
    return attemptSave(doc)

def attemptSave(doc):
    """
    Attempts to save a document
    document: a model instance from the database
    """
    with handleExceptions():
        doc.save()
        return True

@contextmanager
def handleExceptions():
    try:
        yield # body of the with statement effectively runs here
    except Exception as e:
        abort(400, message=str(e))

@auth.verify_password
def verify_password(username, password):
    """
    Uses HTTP Basic Auth (switch to JWT down the road)
    """
    g.username = None
    query_set = models.User.objects(username=username)
    if query_set:
        if helpers.verify(password, query_set[0].password):
            g.username = username
            return True
        else:
            abort(401) # Unauthorized
    else:
        abort(401) # Unauthorized

def checkSiteRole(username, role):
    """
    Checks a user against a site role
    user:       a string corresponding to a username
    role:       a string corresponding to a role (specified in models.py)
    Returns True if the user has the privilege, False otherwise
    """
    query_set = models.User.objects(username=username)
    if not query_set:
        return False
    else:
        user = query_set[0]
        if role in user["site_roles"]:
            if not user["site_roles"][role]:
                return False
        else:
            return False
        return True

def checkProjectRole(username, project_id, role):
    """
    Checks a user against a project role
    user:       a string corresponding to a username
    project_id: a string / id corresponding to a project
    role:       a string corresponding to a role (specified in models.py)
    Returns True if the user has the privilege, False otherwise
    """
    # get project
    query_project = models.Project.objects(id=project_id)
    if not query_project:
        return False
    project = query_project[0]

    # get user
    query_user = models.User.objects(username=username)
    if not query_user:
        return False
    user = query_user[0]

    # check user against project
    if role in project["project_roles"]:
        if user not in project["project_roles"][role]:
            return False
    else:
        return False

    # if passed all checks
    return True

api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<string:doc_id>')
api.add_resource(Projects, '/api/projects')
api.add_resource(Project, '/api/projects/<string:doc_id>')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True) # turn off debug for production
