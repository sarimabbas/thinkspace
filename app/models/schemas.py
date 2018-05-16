from . import models

from marshmallow_sqlalchemy import ModelSchema
from marshmallow import Schema, fields, pprint
from datetime import datetime

class User(ModelSchema):
    class Meta:
        ordered = True
        model = models.User

class Project(ModelSchema):
    comments = fields.Nested("Comment", many=True)
    class Meta:
        ordered = True
        model = models.Project

class Comment(ModelSchema):
    # over-riding to expand the id's to users
    user = fields.Nested(User, only=["username", "first_name", "last_name"])
    class Meta:
        ordered = True
        model = models.Comment
