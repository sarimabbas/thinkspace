import os
import re
import sys
import json
import pprint

from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource

from mongoengine import *
from models import *

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)
api = Api(app)

# connect to the database (currently mongodb, hoping for postgres later)
app.config["DATABASE_URI"] = os.environ.get("MONGODB_URI")
db = connect(db="thinkspace", host=app.config["DATABASE_URI"])

# client
def createTestModels():
    links = Links(github= "http://github.com/sarimabbas")
    user = User(email="sarim.abbas@domain.com", username="sarimabbas", first_name="Sarim", last_name="Abbas")
    user.links = links
    user.hearts = 30
    user.save()

    project = Project(title="Steeped Coffee")
    project.subtitle = "Easiest way to make a cup of coffee, any time, in minutes."
    project.hearts = 133
    project.save()

@app.route("/")
def index():
    # createTestModels()
    return "Hello world!"

# API
def mongo2json(mobjects):
    json_data = mobjects.to_json()
    dicts = json.loads(json_data)
    return dicts

class APIProjects(Resource):
    def get(self):
        query_set = Project.objects
        return mongo2json(query_set)

class APIProject(Resource):
    def get(self, doc_id):
        query_set = Project.objects(id=doc_id)
        return mongo2json(query_set)

class APIUsers(Resource):
    def get(self):
        query_set = User.objects
        return mongo2json(query_set)

class APIUser(Resource):
    def get(self, doc_id):
        query_set = User.objects(id=doc_id)
        return mongo2json(query_set)

api.add_resource(APIUsers, '/api/users')
api.add_resource(APIUser, '/api/users/<string:doc_id>')
api.add_resource(APIProjects, '/api/projects')
api.add_resource(APIProject, '/api/projects/<string:doc_id>')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # turn off debug for production
