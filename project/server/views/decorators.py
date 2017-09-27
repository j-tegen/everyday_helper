from functools import wraps
from flask import request, g, make_response, jsonify
from project.server.models import User, Account

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response
        try:
            auth_header = request.headers.get('Authorization')
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            responseObject = {
                'status': 'fail',
                'message': 'Bearer token malformed.'
            }
            return make_response(jsonify(responseObject)), 401
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, str):
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        g.user_id = resp['sub']
        g.account_id = resp['account']
        return f(*args, **kwargs)
    return decorated_function
