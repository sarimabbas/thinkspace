import os
import re
import json
import pprint
from flask import Flask

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)

@app.route("/")
def hello():
    pp.pprint(os.environ)
    pp.pprint(process.env.MONGOLAB_URI)
    return "Hello world!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
