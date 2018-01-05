import datetime
from mongoengine import *

# EmbeddedDocument : cannot exist independently
# ReferenceField : allows reuse / referencing of a class
# Inherited Classes : allows specialisation of a class

# extensible class to define permissions, user-centric
# for e.g. grant advanced API access, admin privileges etc.
class SiteRoles(EmbeddedDocument):
    curator = BooleanField(default=False)
    admin = BooleanField(default=False)

# extensible class to define permissions, project-centric (which explains the lists)
# for e.g. adding updates, updating description, adding new users
class ProjectRoles(EmbeddedDocument):
    leaders = ListField(ReferenceField("User"))
    founders = ListField(ReferenceField("User"))

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
    username = StringField(max_length=50, required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    image = ImageField()
    links = EmbeddedDocumentField(Links)
    projects = ListField(ReferenceField("Project")) # as per docs, pending definitions are quoted
    hearts = IntField()
    hearted = ListField(ReferenceField("Project"))
    created = DateTimeField(default=datetime.datetime.utcnow)
    site_roles = EmbeddedDocumentField(SiteRoles)
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
    title = StringField(max_length=40, required=True)
    subtitle = StringField()
    category = StringField()
    users = ListField(ReferenceField(User)) # all users, irrespective of permissions
    project_roles = EmbeddedDocumentField(ProjectRoles) # list of users organised by permissions
    comments = ListField(EmbeddedDocumentField(Comment))
    updates = ListField(EmbeddedDocumentField(Update))
    created = DateTimeField(default=datetime.datetime.utcnow)
    hearts = IntField()
