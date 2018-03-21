import json
from passlib.apps import custom_app_context as pwd_context
from mongoengine import *
from bson.objectid import ObjectId

# security
def hash(plaintext):
    return pwd_context.hash(plaintext)

def verify(plaintext, hashed):
    return pwd_context.verify(plaintext, hashed)

# readability
def exception2json(e):
    output = { "messages" : {} }
    for key in e.errors:
        output["messages"][key] = []
        output["messages"][key].append(str(e.errors[key]))
    return output

def mongo2json(model_objects):
    """
    
    """
    json_data = model_objects.to_json()
    dicts = json.loads(json_data)
    return dicts

def isValidId(str):
    if(ObjectId.is_valid(str)):
        return True
    else:
        return False
