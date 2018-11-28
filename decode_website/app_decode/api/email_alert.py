from app_decode import basic_auth
from app_decode.api import bp
from app_decode.models import User, EmailSettings

import json
import re
import smtplib
from email.mime.text import MIMEText

from flask import current_app, request
from flask import jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest

# This is the implementation of the server side of email alert system
# See the API documentation before modifying this file
# Do NOT break existing behaviors if you don't control and can't modify all clients

@basic_auth.login_required
@bp.route('/email_alert', methods=['POST'])
def email_alert():
    if basic_auth.username() != current_app.config['EMAIL_USER_USERNAME']:
        return make_response(jsonify({'error': 'Forbidden'}), 403)
    try:
        supervisor_report, configs, messages = load_request_and_config()
    except BadRequest:
        return make_response(jsonify({'error': 'Invalid json data'}), 400)
    except AttributeError:
        return make_response(jsonify({'error': 'No admin config available'}), 500)
    except KeyError as e:
        return make_response(jsonify({'error': 'Failed to retrieve required key: ' + str(e)}), 400)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    try:
        invalid_ids = {} if messages['ignore_invalid_ids'] else None
        decode_ids(messages, invalid_ids)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except SQLAlchemyError:
        return make_response(jsonify({'error': 'Internal Database Error'}), 500)
    try:
        send_email(configs, messages, supervisor_report)
    except (ConnectionRefusedError, smtplib.SMTPConnectError):
        return make_response(jsonify({'error': 'Cannot access the mail server ' + configs['smtp_host']}), 500)
    except smtplib.SMTPAuthenticationError:
        return make_response(jsonify({'error': 'Mail server authentication failed'}), 400)
    except smtplib.SMTPException as e:
        return make_response(jsonify({'error': 'Cannot send emails because a SMTP excetion was rasied: ' + str(e)}), 500)
    response = invalid_ids if invalid_ids else {}
    response['status'] = 'Success'
    return make_response(jsonify(response), 200)


def load_request_and_config():
    configs = {}
    messages = {}
    admin_config = EmailSettings.query.first()
    if admin_config:
        configs['email_address_regex'] = admin_config.email_address_regex
        configs['SMTP'] = smtplib.SMTP_SSL if admin_config.use_ssl else smtplib.SMTP
        configs['smtp_host'] = admin_config.smtp_host
        configs['smtp_port'] = admin_config.smtp_port
        configs['sender_address'] = admin_config.sender_address
        configs['test_receiver'] = admin_config.test_receiver
        configs['supervisor_address'] = admin_config.supervisor_address
    else:
        raise AttributeError
    data = request.get_json()
    if data is None:
        raise BadRequest
    configs['login_required'] = data['login_required']
    if configs['login_required']:
        configs['sender_username'] = data['sender_username']
        configs['sender_password'] = data['sender_password']    
    messages['messages'] = data['messages']
    messages['user_ids'] = data['user_ids']
    messages['subjects'] = data['subjects']
    messages['ignore_invalid_ids'] = data['ignore_invalid_ids']
    supervisor_report = check_receiver_and_messages(messages, configs)
    return supervisor_report, configs, messages


def check_receiver_and_messages(messages, configs):
    email_address_rule = re.compile(configs['email_address_regex'])
    supervisor_report = []
    for receiver in messages['messages']:
        supervisor_report.append(receiver)
        check_result = email_address_rule.search(receiver)
        if check_result is None or email_address_rule.search(receiver).string != receiver:
            raise ValueError(receiver + ' is not an authorized receiver email address')
        if receiver in messages['user_ids'] and receiver in messages['subjects']:
            if len(messages['user_ids']) != 0:
                continue
        raise ValueError(receiver + ' has no corresponding subject or user_id list')
    return supervisor_report


def decode_ids(messages, invalid_ids):
    for receiver in messages['messages']:
        for user_id in messages['user_ids'][receiver]:
            user = User.query.filter_by(user_id=user_id).first()
            if user is None:
                if messages['ignore_invalid_ids']:
                    messages['messages'][receiver] = messages['messages'][receiver].replace(user_id + '<br>', '')
                    if receiver in invalid_ids:
                        invalid_ids[receiver].append(user_id)
                    else:
                        invalid_ids[receiver] = []
                        invalid_ids[receiver].append(user_id)
                else:
                    raise ValueError(user_id + ' not found in database')
            else:
                messages['messages'][receiver] = messages['messages'][receiver].replace(user_id, user.real_id)


def send_email(configs, messages, supervisor_report):
    with configs['SMTP'](configs['smtp_host'], port=configs['smtp_port']) as smtp_server:
        if configs['login_required']:
            smtp_server.login(configs['sender_username'], configs['sender_password'])
        for receiver, message in messages['messages'].items():
            email = MIMEText(message, 'html', 'utf-8')
            email['Subject'] = messages['subjects'][receiver]
            email['From'] = configs['sender_address']
            email['To'] = configs['test_receiver'] if configs['test_receiver'] else receiver
            smtp_server.send_message(email)
        if configs['supervisor_address']:
            supervisor_email = MIMEText('\n'.join(supervisor_report), 'plain', 'utf-8')
            supervisor_email['Subject'] = 'Email alerts sent successfully to the following addresses'
            supervisor_email['From'] = configs['sender_address']
            supervisor_email['To'] = configs['supervisor_address']
            smtp_server.send_message(supervisor_email)
