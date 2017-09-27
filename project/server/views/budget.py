from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server.models import Budget, BudgetItem, User
from project.server import app, db
from project.server.views.decorators import login_required


bp_budget = Blueprint('budget', __name__)


@bp_budget.route('/budget/', methods=['GET'])
@login_required
def get_all_budget():
    budgets = Budget.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'data': [budget.serialize() for budget in budgets]
    }
    return make_response(jsonify(responseObject)), 200

@bp_budget.route('/budget/<id>/', methods=['GET'])
@login_required
def get_budget(id):
    budget = Budget.query.filter_by(id=id, account_id=g.account_id).first()
    
    if budget:
        responseObject = {
            'status': 'success',
            'data': budget.serialize(2)
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such budget exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_budget.route('/budget/', methods=['POST'])
@login_required
def create_budget():
    post_data = request.get_json()
    try:
        budget = Budget(user_id=g.user_id, account_id=g.account_id, data=post_data)
        db.session.add(budget)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a budget',
                'data': budget.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400

 
@bp_budget.route('/budget/<id>/budget_item/', methods=['POST'])
@login_required
def create_budget_item(id):
    post_data = request.get_json()
    try:
        budget = Budget.query.filter_by(id=id, account_id=g.account_id).first()
        budget_item = BudgetItem.query.filter(
            BudgetItem.year==post_data.get('year')
        ).filter( 
            BudgetItem.month==post_data.get('month')
        ).filter(
            BudgetItem.category_id==post_data.get('category').get('id')
        ).first()
        
        # Already exists
        if budget_item:
            responseObject = {
                    'status': 'fail',
                    'message': 'Budget_item already exists'
                }
            return make_response(jsonify(responseObject)), 409

        budget_item = BudgetItem(account_id=g.account_id, data=post_data)
        
        budget.budget_items.append(budget_item)
        
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a budget_item',
                'data': budget_item.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400


@bp_budget.route('/budget_item/<id>/', methods=['GET'])
@login_required
def get_budget_item(id):
    budget_item = BudgetItem.query.get(id)
    
    if budget_item:
        responseObject = {
            'status': 'success',
            'data': budget_item.serialize()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such budget_item exists'
        }
        return make_response(jsonify(responseObject)), 404
