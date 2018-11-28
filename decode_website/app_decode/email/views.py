from app_decode import basic_auth, db
from app_decode.email import bp
from app_decode.models import Admin, EmailSettings

from flask import abort, current_app, make_response, render_template, request
from passlib.hash import pbkdf2_sha256

@bp.route('/')
@basic_auth.login_required
def dashboard():
    if basic_auth.username() != current_app.config['EMAIL_ADMIN_USERNAME']:
        abort(403)
    templates = {}
    templates['email_admin_username'] = current_app.config['EMAIL_ADMIN_USERNAME']
    templates['email_user_username'] = current_app.config['EMAIL_USER_USERNAME']
    settings = EmailSettings.query.first()
    templates['smtp_host'] = settings.smtp_host
    templates['smtp_port'] = settings.smtp_port
    templates['use_ssl_true'] = 'checked' if settings.use_ssl else ''
    templates['use_ssl_false'] = '' if settings.use_ssl else 'checked'
    templates['sender_address'] = settings.sender_address
    templates['test_receiver'] = settings.test_receiver
    templates['email_address_regex'] = settings.email_address_regex
    templates['supervisor_address'] = settings.supervisor_address
    return render_template('/email/email_index.html', **templates)


@bp.route('/password', methods=['POST'])
@basic_auth.login_required
def change_password():
    if basic_auth.username() != current_app.config['EMAIL_ADMIN_USERNAME']:
        abort(403)
    username = request.form['username']
    if username not in [current_app.config['EMAIL_ADMIN_USERNAME'], current_app.config['EMAIL_USER_USERNAME']]:
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


@bp.route('/settings', methods=['POST'])
@basic_auth.login_required
def settings():
    if basic_auth.username() != current_app.config['EMAIL_ADMIN_USERNAME']:
        abort(403)
    settings = EmailSettings.query.first()
    settings.smtp_host = request.form['smtp_host']
    settings.smtp_port = request.form['smtp_port']
    settings.use_ssl = True if request.form['use_ssl'] == 'true' else False
    settings.sender_address = request.form['sender_address']
    settings.test_receiver = request.form['test_receiver']
    settings.email_address_regex = request.form['email_address_regex']
    settings.supervisor_address = request.form['supervisor_address']
    db.session.commit()
    return make_response('All settings have been updated successfully.')
