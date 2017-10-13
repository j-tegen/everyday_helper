from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView
from sqlalchemy import func

from project.server import bcrypt, db
from project.server.models import User, Account, BlacklistToken
from project.server.views.decorators import login_required

bp_user = Blueprint('user', __name__)

@bp_user.route('/user/register/', methods=['POST'])
def user_register():
    post_data = request.get_json()
    # check if user already exists
    user = User.query.filter(func.lower(User.email) == func.lower(post_data.get('email'))).first()
    if not user:
        try:
            user = User(
                username=post_data.get('username'),
                email=post_data.get('email'),
                password=post_data.get('password'),
                name=post_data.get('name')
            )

            account = Account.query.filter(func.lower(Account.account_name) == func.lower(post_data.get('account_name'))).first()
            if not account:
                account = Account(account_name=post_data.get('account_name'))
                db.session.add(account)

                user.verified = True
            
            account.users.append(user)
            # insert the user
            # db.session.add(user)
            db.session.commit()
            # generate the auth token
            auth_token = user.encode_auth_token(user.id, user.account_id)
            print(auth_token)
            responseObject = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode(),
                'user': user.serialize()
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
            'user': user.serialize()
        }
        return make_response(jsonify(responseObject)), 409

@bp_user.route('/user/login/', methods=['POST'])
def user_login():
    post_data = request.get_json()
    try:
        # fetch the user data
        user = User.query.filter(
            func.lower(User.email) == func.lower(post_data.get('email'))
        ).first()
        if user and bcrypt.check_password_hash(
            user.password, post_data.get('password')
        ):
            auth_token = user.encode_auth_token(user.id, user.account_id)
            if auth_token:
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token.decode(),
                    'user': user.serialize()
                }
                return make_response(jsonify(responseObject)), 200
        elif not user:
            responseObject = {
                'status': 'fail',
                'message': 'Invalid password and/or username and account.'
            }
            return make_response(jsonify(responseObject)), 404
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'message': 'Try again'
        }
        return make_response(jsonify(responseObject)), 500

@bp_user.route('/user/', methods=['GET'])
@login_required
def get_active_user():
    user = User.query.get(g.user_id)
    responseObject = user.serialize()
    return make_response(jsonify(responseObject)), 200

@bp_user.route('/users/', methods=['GET'])
@login_required
def get_all_users():
    users = User.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'data': [user.serialize() for user in users]
    }
    return make_response(jsonify(responseObject)), 200

@bp_user.route('/user/logout/', methods=['POST'])
def user_logout():
    # get auth token
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                return make_response(jsonify(responseObject)), 200
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': e
                }
                return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 403