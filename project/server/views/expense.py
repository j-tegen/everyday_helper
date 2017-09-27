from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server.models import Expense, BudgetItem, User
from project.server import app, db
from project.server.views.decorators import login_required


bp_expense = Blueprint('expense', __name__)


@bp_expense.route('/expense/', methods=['GET'])
@login_required
def get_all_expense():
    expenses = Expense.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'data': [expense.serialize() for expense in expenses]
    }
    return make_response(jsonify(responseObject)), 200

@bp_expense.route('/expense/<id>/', methods=['GET'])
@login_required
def get_expense(id):
    expense = Expense.query.get(id)
    
    if expense:
        responseObject = {
            'status': 'success',
            'data': expense.serialize()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such expense exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_expense.route('/expense/', methods=['POST'])
@login_required
def create_expense():
    post_data = request.get_json()
    try:
        expense = Expense(data=post_data)
        expense.add_to_budget_item()
        db.session.add(expense)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a expense',
                'data': expense.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400
