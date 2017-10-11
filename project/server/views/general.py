from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server import app, db
from project.server.views.decorators import login_required


bp_general = Blueprint('general', __name__)


@bp_general.route('/general/status/', methods=['GET'])
def status():
    
    responseObject = {
        'status': 'success',
        'message': "It's aliiiiive!" 
    }
    return make_response(jsonify(responseObject)), 200
