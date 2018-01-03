import os
import re
import sys
import json
import pprint

# helper functions
import helpers
# models for storing data in mongodb (may consider postgres later)
import models
# flask web framework
from flask import Flask, g, request
# flask extension for easy API endpoint creation
from flask_restful import abort, Api, Resource
# flask extension for authentication
from flask_httpauth import HTTPBasicAuth
# ODM for mongodb
from mongoengine import *

# connections
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.config["DATABASE_URI"] = os.environ.get("MONGODB_URI")
db = connect(db="thinkspace", host=app.config["DATABASE_URI"])

pp = pprint.PrettyPrinter(indent=4)

@app.route("/")
def index():
    print(models.User.objects(Q(username="testdoe") | Q(email="sarim.abbas@domain.com")), file=sys.stderr)
    return "Hello world!"

@app.route("/createtestuser")
def createTestUser():
    links = models.Links(github="http://facebook.com/testdoe3")
    user = models.User(email="test.doe3@domain.com", username="testdoe4", first_name="TEST2", last_name="DOE2")
    user.links = links
    user.hearts = 54
    user.password = helpers.hash("hello")
    user.site_roles = models.SiteRoles()
    user.save()
    return "success"

@app.route("/createtestproject")
def createTestProject():
    project = models.Project(title="Unsteeped Coffee")
    project.subtitle = "Hardest way to make a cup of coffee, any time, in minutes."
    project.hearts = 0
    project.save()
    return "success"

### API
## HTTP Basic Auth (switch to JWT down the road)
@auth.verify_password
def verify_password(username, password):
    g.user = None
    query_set = models.User.objects(username=username)
    if query_set:
        if helpers.verify(password, query_set[0].password):
            g.user = username
            return True
    else:
        return False

def mongo2json(model_objects):
    json_data = model_objects.to_json()
    dicts = json.loads(json_data)
    return dicts

class Projects(Resource):
    # visibility: founders, admin
    @auth.login_required
    def get(self):
        print(g.user, file=sys.stderr)
        query_set = models.Project.objects
        for key in query_set[0]:
            print(key, file=sys.stderr)
        return mongo2json(query_set)

class Project(Resource):
    # access: public
    def get(self, doc_id):
        query_set = models.Project.objects(id=doc_id)
        return mongo2json(query_set)

    # access: project leaders, founders and site curators, admin
    # intended for updates (for project creation, send POST to /projects)
    def put(self, doc_id):
        webargs = request.json
        query_set = models.Project.objects(id=doc_id)
        # if the project exists
        if query_set:
            project = query_set[0]
            # update the fields
            for key in webargs:
                if key in project and webargs[key]:
                    project[key] = webargs[key]
            # attempt to save
            try:
                project.save()
            except ValidationError as e:
                return helpers.exception2json(e), 422
        # if the project does not exist
        else:
            # construct it
            project = models.Project()
            for key in webargs:
                if webargs[key]:
                    project[key] = webargs[key]
            # attempt to save
            try:
                project.save()
            except ValidationError as e:
                return helpers.exception2json(e), 422
        return mongo2json(project), 201

    # access: project leaders, founders and site curators, admin
    def delete(self, doc_id):
        query_set = models.Project.objects(id=doc_id)
        # if the project exists
        if query_set:
            project = query_set[0]
            project.delete()
        return "", 204

class Users(Resource):
    # visibility: API is public but hashed password is not returned
    def get(self):
        query_set = models.User.objects.exclude("password")
        return mongo2json(query_set)

class User(Resource):
    # visibility: API is public but hashed password is not returned
    def get(self, doc_id):
        query_set = models.User.objects(id=doc_id).exclude("password")
        return mongo2json(query_set)

api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<string:doc_id>')
api.add_resource(Projects, '/api/projects')
api.add_resource(Project, '/api/projects/<string:doc_id>')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # turn off debug for production
