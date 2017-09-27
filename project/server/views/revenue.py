from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server.models import Revenue, BudgetItem, User
from project.server import app, db
from project.server.views.decorators import login_required


bp_revenue = Blueprint('revenue', __name__)


@bp_revenue.route('/revenue/', methods=['GET'])
@login_required
def get_all_revenue():
    revenues = Revenue.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'data': [revenue.serialize() for revenue in revenues]
    }
    return make_response(jsonify(responseObject)), 200

@bp_revenue.route('/revenue/<id>/', methods=['GET'])
@login_required
def get_revenue(id):
    revenue = Revenue.query.get(id)
    
    if revenue:
        responseObject = {
            'status': 'success',
            'data': revenue.serialize()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such revenue exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_revenue.route('/revenue/', methods=['POST'])
@login_required
def create_revenue():
    post_data = request.get_json()
    try:
        revenue = Revenue(data=post_data)
        revenue.add_to_budget_item()
        db.session.add(revenue)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a revenue',
                'data': revenue.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400
