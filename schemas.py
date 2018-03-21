import models
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import Schema, fields, pprint
from datetime import datetime

class User(ModelSchema):
    class Meta:
        ordered = True
        model = models.User

class Project(ModelSchema):
    class Meta:
        ordered = True
        model = models.Project
