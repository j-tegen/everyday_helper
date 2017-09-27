from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server.models import Category, User
from project.server import app, db
from project.server.views.decorators import login_required


bp_category = Blueprint('category', __name__)


@bp_category.route('/category/', methods=['GET'])
@login_required
def get_all_category():
    categories = Category.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'data': [category.serialize(0) for category in categorys]
    }
    return make_response(jsonify(responseObject)), 200


@bp_category.route('/category/<id>/', methods=['GET'])
@login_required
def get_category(id):
    category = Category.query.filter_by(id=id, account_id=g.account_id).first()
    
    if category:
        responseObject = {
            'status': 'success',
            'data': category.serialize(0)
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such category exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_category.route('/category/<id>/', methods=['PUT'])
@login_required
def update_category(id):
    put_data = request.get_json()
    category = Category.query.filter_by(id=id, account_id=g.account_id).first()
    
    if category:
        category.name = put_data.get('name')
        db.session.commit()
        responseObject = {
            'status': 'success',
            'data': category.serialize(0)
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such category exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_category.route('/category/', methods=['POST'])
@login_required
def create_category():
    post_data = request.get_json()
    try:
        category = Category(g.account_id, post_data)
        db.session.add(category)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created a category',
                'data': category.serialize(0)
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400
