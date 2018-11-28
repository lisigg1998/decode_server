from flask import Flask, make_response, jsonify
from app_decode.config import Config
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

import click

app_decode = Flask(__name__)
app_decode.config.from_object(Config)
basic_auth = HTTPBasicAuth()
db = SQLAlchemy(app_decode)
migrate = Migrate(app_decode, db)

from app_decode.api import bp as tokens_bp
app_decode.register_blueprint(tokens_bp, url_prefix='/api')

from app_decode.admin import bp as admin_bp
app_decode.register_blueprint(admin_bp, url_prefix='/admin')

from app_decode.email import bp as email_bp
app_decode.register_blueprint(email_bp, url_prefix='/email')

from app_decode import routes, models

@basic_auth.verify_password
def verify_password(username, password):
    user = models.Admin.query.filter_by(username=username).first()
    if not user:
        user = models.DecodeUser.query.filter_by(username=username).first()
        if not user:
            return False
    return pbkdf2_sha256.verify(password, user.password_hash)


@basic_auth.error_handler
def basic_auth_error():
    return make_response(jsonify({'error': 'Unauthorized'}), 401)


@app_decode.cli.command()
def initdb():
    initial_admins = ['ADMIN_PORTAL', 'ISSUE_TOKEN', 'VERIFY_TOKEN', 'EMAIL_ADMIN', 'EMAIL_USER']
    for x in initial_admins:
        username = app_decode.config[x + '_USERNAME']
        password_hash = pbkdf2_sha256.hash(app_decode.config[x + '_PASSWORD'])
        user = models.Admin.query.filter_by(username=username).first()
        if user:
            click.echo('Failed to initialize ' + x + ' because it already exists.')
        else:
            user = models.Admin(username=username, password_hash=password_hash)
            db.session.add(user)
    email_settings = models.EmailSettings.query.all()
    if email_settings:
        click.echo('Failed to initialize email settings - they have already been created.')
    else:
        email_settings = models.EmailSettings(smtp_host='localhost', smtp_port=25, use_ssl=False,
                                              sender_address='test@sribd.cn', test_receiver='test@sribd.cn',
                                              email_address_regex='^[a-zA-Z]+@cuhk\\.edu\\.cn$',
                                              supervisor_address='', pri_key=0)
        db.session.add(email_settings)
    db.session.commit()
