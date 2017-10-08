from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server.models import ShoppingList, ShoppingListItem, User
from project.server import app, db
from project.server.views.decorators import login_required


bp_shopping_list = Blueprint('shopping_list', __name__)


@bp_shopping_list.route('/shopping_list/', methods=['GET'])
@login_required
def get_all_shopping_list():
    shopping_lists = ShoppingList.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'data': [shopping_list.serialize() for shopping_list in shopping_lists]
    }
    return make_response(jsonify(responseObject)), 200

@bp_shopping_list.route('/shopping_list/<id>/', methods=['GET'])
@login_required
def get_shopping_list(id):
    shopping_list = ShoppingList.query.filter_by(id=id, account_id=g.account_id).first()
    
    if shopping_list:
        responseObject = {
            'status': 'success',
            'data': shopping_list.serialize()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such shopping_list exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_shopping_list.route('/shopping_list/', methods=['POST'])
@login_required
def create_shopping_list():
    post_data = request.get_json()
    try:
        shopping_list = ShoppingList(user_id=g.user_id, account_id=g.account_id, data=post_data)
        db.session.add(shopping_list)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a shopping_list',
                'data': shopping_list.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400

@bp_shopping_list.route('/shopping_list/<id>/', methods=['PUT'])
@login_required
def update_shopping_list(id):
    put_data = request.get_json()
    try:
        shopping_list = ShoppingList.query.get(id)
        if shopping_list.category_id != put_data.get('category_id'):
            shopping_list_items = ShoppingListItem.query.filter_by(shopping_list_id=shopping_list.id,
                category_id=shopping_list.category_id).all()
            
            for item in shopping_list_items:
                item.category_id = put_data.get('category_id')
                db.session.add(item)

        shopping_list.update(put_data) 
        db.session.add(shopping_list)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a shopping_list',
                'data': shopping_list.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400
 
@bp_shopping_list.route('/shopping_list/<id>/shopping_list_item/', methods=['POST'])
@login_required
def create_shopping_list_item(id):
    post_data = request.get_json()
    try:
        shopping_list = ShoppingList.query.filter_by(id=id, account_id=g.account_id).first()
        if shopping_list:
            category_id = post_data.get('category', {}).get('id', None)
            shopping_list_item = ShoppingListItem(shopping_list_id=shopping_list.id, category_id=category_id, data=post_data)
            db.session.add(shopping_list_item)
            db.session.commit()
            responseObject = {
                    'status': 'success',
                    'message': 'Successfully created a shopping_list',
                    'data': shopping_list_item.serialize()
                }
            return make_response(jsonify(responseObject)), 201
        else:
            responseObject = {
                    'status': 'fail',
                    'message': 'No such shopping_list.'
                }
            return make_response(jsonify(responseObject)), 404    
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400


@bp_shopping_list.route('/shopping_list_item/<id>/', methods=['GET'])
@login_required
def get_shopping_list_item(id):
    shopping_list_item = ShoppingListItem.query.get(id)
    
    if shopping_list_item:
        responseObject = {
            'status': 'success',
            'data': shopping_list_item.serialize()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such shopping_list_item exists'
        }
        return make_response(jsonify(responseObject)), 404