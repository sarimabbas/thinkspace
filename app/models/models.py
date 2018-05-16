from datetime import datetime
from app import db

# a helper table that matches projects to its members
project_member = db.Table('project_member',
    db.Column('project_id', db.Integer(), db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True)
)

# a helper table that matches projects to its administrators
project_admin = db.Table('project_admin',
    db.Column('project_id', db.Integer(), db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True)
)

# a helper table that matches projects to the users that hearted it
project_heart = db.Table('project_heart',
    db.Column('project_id', db.Integer(), db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True)
)

# a helper table that matches projects to their tags
project_tag = db.Table('project_tag',
    db.Column('project_id', db.Integer(), db.ForeignKey('project.id'), primary_key=True),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id'), primary_key=True)
)

# a helper table that matches users to the users that hearted them
user_heart = db.Table('user_heart',
    db.Column('hearter_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True),
    db.Column('heartee_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    ## basic
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    hearts = db.Column(db.Integer(), default=0)
    site_admin = db.Column(db.Boolean(), default=False, nullable=False)
    site_curator = db.Column(db.Boolean(), default=False, nullable=False)
    api_write = db.Column(db.Boolean(), default=False, nullable=False)
    ## relations
    #### one to many
    comments = db.relationship("Comment", backref='user')
    posts = db.relationship("Post", backref='user')
    #### many to many
    hearted_projects = db.relationship("Project", secondary=project_heart)
    project_member = db.relationship("Project", secondary=project_member)
    project_admin = db.relationship("Project", secondary=project_admin)
    #### many to many (self-referential)
    heartees = db.relationship("User", secondary=user_heart, primaryjoin=id ==
                               user_heart.c.hearter_id, secondaryjoin=id == user_heart.c.heartee_id)
    hearters = db.relationship("User", secondary=user_heart, primaryjoin=id ==
                               user_heart.c.heartee_id, secondaryjoin=id == user_heart.c.hearter_id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Project(db.Model):
    ## basic
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    subtitle = db.Column(db.String(), default="")
    description = db.Column(db.String(), default="")
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    hearts = db.Column(db.Integer(), default=0)
    ## relations
    #### many to many
    tags = db.relationship("Tag", secondary=project_tag)
    members = db.relationship("User", secondary=project_member)
    admin = db.relationship("User", secondary=project_admin)
    hearters = db.relationship("User", secondary=project_heart)
    #### one to many (with backrefs for ease of use)
    comments = db.relationship("Comment", backref='project')
    posts = db.relationship("Post", backref='project')

    def __repr__(self):
        return '<Project {}>'.format(self.id)

class Comment(db.Model):
    ## basic
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    ## relations
    #### one to many helpers
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)         # allows for comment.user
    project_id = db.Column(db.Integer(), db.ForeignKey('project.id'), nullable=False)   # allows for comment.project

    def __repr__(self):
        return '<Comment {}>'.format(self.id)

class Post(db.Model):
    ## basic
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    ## relations
    #### one to many helpers
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)         # allows for post.user
    project_id = db.Column(db.Integer(), db.ForeignKey('project.id'), nullable=False)   # allows for post.project

    def __repr__(self):
        return '<Post {}>'.format(self.id)

class Tag(db.Model):
    ## basic
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(), nullable=False)
    ## relations
    #### many to many
    projects = db.relationship("Project", secondary=project_tag)

    def __repr__(self):
        return '<Tag {}>'.format(self.text)
