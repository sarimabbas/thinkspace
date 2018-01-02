import os
import re
import json
import pprint

from flask import Flask
from flask.ext import restful

from mongoengine import *
from models import *

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)
api = restful.Api(app)

# connect to the database (currently mongodb, hoping for postgres later)
app.config["DATABASE_URI"] = os.environ.get("MONGODB_URI")
db = connect(db="thinkspace", host=app.config["DATABASE_URI"])

# client
@app.route("/")
def index():
    return "Hello world!"

# API
class Test(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/user/<string:username>')
api.add_resource(Test, '/api/test')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # turn off debug for production
