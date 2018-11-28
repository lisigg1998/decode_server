from app_decode import db
from app_decode import basic_auth
from app_decode.api import bp
from app_decode.models import User, Token

import datetime as dt
import secrets

from flask import current_app, request
from flask import jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError

# This is the implementation of the token issue and token verify API
# See the API documentations before modifying this file
# Do NOT break existing behaviors if you don't control and can't modify all clients

@bp.route('/tokens/<string:real_id>', methods=['POST'])
@basic_auth.login_required
def issue_token(real_id):
    if basic_auth.username() != current_app.config['ISSUE_TOKEN_USERNAME']:
        return make_response(jsonify({'error': 'Forbidden'}), 403)
    try:
        user = User.query.get(real_id)
        if user is None:
            return make_response(jsonify({'error': 'User not found'}), 400)
        user_id = user.user_id
        return make_response(jsonify({'user_id': user_id, 'token': generate_token(user_id)}), 200)
    except SQLAlchemyError:
        return make_response(jsonify({'error': 'Database error'}), 500)


@bp.route('/tokens/<string:user_id>', methods=['GET'])
@basic_auth.login_required
def verify_token(user_id):
    if basic_auth.username() != current_app.config['VERIFY_TOKEN_USERNAME']:
        return make_response(jsonify({'error': 'Forbidden'}), 403)
    try:
        token = Token.query.get(user_id)
        if token is None or token.token != request.args.get('token') or token.expiration <= dt.datetime.now():
            response = make_response(jsonify({'status': 'Invalid'}), 400)
        else:
            response = make_response(jsonify({'status': 'Success'}), 200)
    except SQLAlchemyError:
        response = make_response(jsonify({'status': 'Database error'}), 500)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def generate_token(user_id):
    """Return a cryptographically secure url token.
    The token contains TOKEN_N_BYTES random bytes.
    The token will be upserted into database with
    its expiration timestamp before returned."""
    token = secrets.token_urlsafe(current_app.config['TOKEN_N_BYTES'])
    expiration = dt.datetime.now() + dt.timedelta(0, current_app.config['TOKEN_LIFESPAN'])
    token_object = Token(user_id=user_id, token=token, expiration=expiration)
    db.session.merge(token_object)
    db.session.commit()
    return token
