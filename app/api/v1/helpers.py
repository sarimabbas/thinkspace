import app.models as models

from sqlalchemy.orm import joinedload
from webargs import ValidationError
from passlib.apps import custom_app_context as pwd_context

# security

def passwordHash(plaintext):
    return pwd_context.hash(plaintext)

def passwordVerify(plaintext, hashed):
    return pwd_context.verify(plaintext, hashed)

# permissions

def hasSitePrivileges(username):
    user = models.User.query.filter_by(username=username).first()
    if user.site_admin or user.api_write:
        return True
    else:
        return False

def hasProjectPrivileges(username, project_id):
    user = models.User.query.filter_by(username=username).first()
    project = models.Project.query.options(joinedload('admin')).get(project_id)
    if user in project.admin:
        return True
    else:
        return False

# validators

def userIdDoesNotExist(val):
    user = models.User.query.get(val)
    if user is None:
        raise ValidationError(
            "No user exists with this id.")

def projectIdDoesNotExist(val):
    project = models.Project.query.get(val)
    if project is None:
        raise ValidationError(
            "No project exists with this id.")

def usernameDoesNotExist(val):
    user = models.User.query.filter_by(username=val).first()
    if user is None:
        raise ValidationError(
            "No user exists with this username.")

def manyUsernamesDoNotExist(vals):
    for val in vals:
        user = models.User.query.filter_by(username=val).first()
        if user is None:
            raise ValidationError(
                "One or more users with the given usernames do not exist.")

def emailDoesNotExist(val):
    user = models.User.query.filter_by(email=val).first()
    if user is None:
        raise ValidationError(
            "No user exists with this email address.")

def tagDoesNotExist(val):
    tags = models.Tag.query.all()
    tag_strs = []
    for tag in tags:
        tag_strs.append(tag.text)
    for key in val:
        if key not in tag_strs:
            raise ValidationError(
                "One or more of your chosen tags do not exist.")

def usernameExists(val):
    user = models.User.query.filter_by(username=val).first()
    if user is not None:
        raise ValidationError(
            "A user already exists with this username.")

def emailExists(val):
    user = models.User.query.filter_by(email=val).first()
    if user is not None:
        raise ValidationError(
            "A user already exists with this email address.")
