from passlib.apps import custom_app_context as pwd_context

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
