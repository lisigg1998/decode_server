from app_decode import basic_auth, db
from app_decode.admin import bp
from app_decode.models import Admin, DecodeUser, Token, User

from flask import abort, current_app, make_response, render_template, request
from passlib.hash import pbkdf2_sha256

@bp.route('/')
@basic_auth.login_required
def dashboard():
    if basic_auth.username() != current_app.config['ADMIN_PORTAL_USERNAME']:
        abort(403)
    templates = {}
    templates['admin_portal_username'] = current_app.config['ADMIN_PORTAL_USERNAME']
    templates['issue_token_username'] = current_app.config['ISSUE_TOKEN_USERNAME']
    templates['verify_token_username'] = current_app.config['VERIFY_TOKEN_USERNAME']
    templates['decode_users'] = ''
    templates['not_usernames'] = ''
    for x in ['ADMIN_PORTAL', 'ISSUE_TOKEN', 'VERIFY_TOKEN', 'EMAIL_ADMIN', 'EMAIL_USER']:
        templates['not_usernames'] += current_app.config[x + '_USERNAME'] + ', '
    decode_users = DecodeUser.query.all()
    if decode_users:
        for user in decode_users:
            templates['decode_users'] += '\n      <p><strong>' + user.username + '</strong></p>'
    return render_template('/admin/admin_index.html', **templates)


@bp.route('/password', methods=['POST'])
@basic_auth.login_required
def change_password():
    if basic_auth.username() != current_app.config['ADMIN_PORTAL_USERNAME']:
        abort(403)
    username = request.form['username']
    if username not in [current_app.config['ADMIN_PORTAL_USERNAME'],
                        current_app.config['ISSUE_TOKEN_USERNAME'],
                        current_app.config['VERIFY_TOKEN_USERNAME']]:
        abort(400)
    if request.form['pwd'] != request.form['pwd_confirm']:
        return make_response('Two passwords do not match. Try again.')
    if request.form['pwd'] != ''.join(request.form['pwd'].split()):
        return make_response('The password should not contain any whitespace characters.')
    password_hash = pbkdf2_sha256.hash(request.form['pwd'])
    admin = Admin.query.filter_by(username=username).first()
    admin.password_hash = password_hash
    db.session.commit()
    return make_response('The password of ' + username + ' has been changed successfully.')


@bp.route('/decode_user', methods=['POST'])
@basic_auth.login_required
def decode_user():
    if basic_auth.username() != current_app.config['ADMIN_PORTAL_USERNAME']:
        abort(403)
    action = request.form['action']
    username = request.form['username']
    user = DecodeUser.query.filter_by(username=username).first()
    if action == 'delete':
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response('User ' + username + ' has been deleted.')
        else:
            return make_response('The username you want to delete does not exist.')
    elif action == 'update':
        if request.form['pwd'] != request.form['pwd_confirm']:
            return make_response('Two passwords do not match. Try again.')
        if request.form['pwd'] != ''.join(request.form['pwd'].split()):
            return make_response('The password should not contain any whitespace characters.')
        password_hash = pbkdf2_sha256.hash(request.form['pwd'])
        if user:
            user.password_hash = password_hash
        else:
            user = DecodeUser(username=username, password_hash=password_hash)
            db.session.add(user)
        db.session.commit()
        return make_response('User ' + username + ' has been added or updated successfully.')


@bp.route('/uploadcsv', methods=['POST'])
@basic_auth.login_required
def upload_csv():
    if basic_auth.username() != current_app.config['ADMIN_PORTAL_USERNAME']:
        abort(403)
    if 'file' not in request.files or request.files['file'].filename == '':
        return make_response('No file uploaded')
    data = request.files['file']
    if not data.filename.lower().endswith('.csv'):
        return make_response('Not a CSV file')
    rows = data.stream.read().decode("utf-8").split('\n')
    for row in rows:
        row = ''.join(row.split())
        if row:
            modify_user(*row.split(','))
    return make_response('All records have been added or updated.')


@bp.route('/entry', methods=['POST'])
@basic_auth.login_required
def entry():
    if basic_auth.username() != current_app.config['ADMIN_PORTAL_USERNAME']:
        abort(403)
    action = request.form['action']
    real_id = request.form['real_id']
    if action == 'delete':
        record = User.query.filter_by(real_id=real_id).first()
        if record:
            token_record = Token.query.filter_by(user_id=record.user_id).first()
            if token_record:
                db.session.delete(token_record)
            db.session.delete(record)
            db.session.commit()
            return make_response('Record ' + real_id + ' has been deleted.')
        else:
            return make_response('Record ' + real_id + ' does not exist.')
    elif action == 'update':
        modify_user(real_id, request.form['user_id'])
        return make_response('Record ' + real_id + ' has been added or updated.')
    else:
        abort(400)


@bp.route('/clearall', methods=['POST'])
@basic_auth.login_required
def clearall():
    if basic_auth.username() != current_app.config['ADMIN_PORTAL_USERNAME']:
        abort(403)
    Token.query.delete()
    User.query.delete()
    db.session.commit()
    return make_response('All token and user records have been deleted.')


def modify_user(real_id, user_id):
    '''Update the user and its token (if any) if the real ID exists.
       Delete token first to avoid foreign key constraint problems.
       If not, add a new user.'''
    record = User.query.filter_by(real_id=real_id).first()
    if record:
        token_record = Token.query.filter_by(user_id=record.user_id).first()
        if token_record:
            token = token_record.token
            expiration = token_record.expiration
            db.session.delete(token_record)
            db.session.commit()
            record.user_id = user_id
            token_record = Token(user_id=user_id, token=token, expiration=expiration)
            db.session.add(token_record)
        else:
            record.user_id = user_id
    else:
        record = User(real_id=real_id, user_id=user_id)
        db.session.add(record)
    db.session.commit()
