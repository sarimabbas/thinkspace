###########
# imports #
###########

# blueprint for routing
from app.admin import bp

# rendering templates
from flask import render_template

###########################
# single view application #
###########################

@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")