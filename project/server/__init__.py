import os

from flask import Flask, request, make_response, jsonify, g
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from functools import wraps
import project.server.utils

app = Flask(__name__)


app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.json_encoder = utils.CustomJSONEncoder
app.config.from_object(app_settings)

CORS(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


from project.server.views.user import bp_user
from project.server.views.todo import bp_todo
from project.server.views.shopping_list import bp_shopping_list
from project.server.views.category import bp_category
from project.server.views.budget import bp_budget
from project.server.views.expense import bp_expense
from project.server.views.revenue import bp_revenue

app.register_blueprint(bp_user, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(bp_todo, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(bp_shopping_list, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(bp_category, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(bp_budget, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(bp_expense, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(bp_revenue, url_prefix=app.config['APPLICATION_ROOT'])

