import os
import re
import json
import pprint

from flask import Flask
from mongoengine import *
from models import *

pp = pprint.PrettyPrinter(indent=4)

# connect to the database (currently mongodb, hoping for postgres later)
app = Flask(__name__)
print(app.config)
app.config["DATABASE_URI"] = os.environ.get("MONGODB_URI")
db = connect(db="thinkspace", host=app.config["DATABASE_URI"])

@app.route("/")
def hello():

    post1 = TextPost(title='Using MongoEngine', content='See the tutorial')
    post1.tags = ['mongodb', 'mongoengine']
    post1.save()

    yalie = YaleStudent(email="hello@yale.edu", first_name="Sar", last_name="Abb", net_id="sa857")
    yalie.save()

    return "Hello world! {}".format(TextPost.objects.count())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
