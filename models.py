import datetime
from mongoengine import *

# EmbeddedDocument : cannot exist independently
# ReferenceField : allows reuse of a class
# Inherited Classes : allows specialisation of a class

# extensible class to manage external links
class Links(EmbeddedDocument):
    github = URLField()
    linkedin = URLField()
    facebook = URLField()
    twitter = URLField()
    website = URLField()

# generic user class
class User(Document):
    email = EmailField(required=True)
    username = StringField(max_length=50, required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    image = ImageField()
    links = EmbeddedDocumentField(Links)
    projects = ListField(ReferenceField("Project")) # as per docs, undefined documents are quoted
    hearts = IntField()
    hearted = ListField(ReferenceField("Project"))
    created = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'allow_inheritance': True}

# extended user class
class YaleStudent(User):
    net_id = StringField(required=True, max_length=10)

class Comment(EmbeddedDocument):
    commenter = ReferenceField(User) # what happens when a user is deleted?
    content = StringField()
    created = DateTimeField(default=datetime.datetime.utcnow)

class Update(EmbeddedDocument):
    content = StringField()
    created = DateTimeField(default=datetime.datetime.utcnow)

class Project(Document):
    title = StringField(max_length=50)
    subtitle = StringField()
    category = StringField()
    founders = ListField(ReferenceField(User))
    comments = ListField(EmbeddedDocumentField(Comment))
    updates = ListField(EmbeddedDocumentField(Update))
    created = DateTimeField(default=datetime.datetime.utcnow)
    hearts = IntField()
