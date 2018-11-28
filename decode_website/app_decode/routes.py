from app_decode import app_decode
from app_decode import basic_auth
from app_decode.models import User

from flask import abort, current_app, make_response, redirect, render_template, request

@app_decode.route('/')
@basic_auth.login_required
def homepage():
    if (basic_auth.username() == current_app.config['VERIFY_TOKEN_USERNAME']
       or basic_auth.username() == current_app.config['ISSUE_TOKEN_USERNAME']
       or basic_auth.username() == current_app.config['EMAIL_USER_USERNAME']):
        return make_response('', 403)
    elif basic_auth.username() == current_app.config['ADMIN_PORTAL_USERNAME']:
        return redirect('/admin/', 301)
    elif basic_auth.username() == current_app.config['EMAIL_ADMIN_USERNAME']:
        return redirect('/email/', 301)
    else:
        return render_template('query.html')


@app_decode.route('/result', methods=['POST'])
@basic_auth.login_required
def result():
    if (basic_auth.username() == current_app.config['VERIFY_TOKEN_USERNAME']
       or basic_auth.username() == current_app.config['ISSUE_TOKEN_USERNAME']
       or basic_auth.username() == current_app.config['EMAIL_USER_USERNAME']):
        return abort(403)
    encoded_ids = request.form['Encoded_ID_List'].strip().split('\n')
    results = ''
    for i, x in enumerate(encoded_ids):
        x = x.strip()
        results += ('\t<tr>\n\t\t<td>' + str(i + 1).zfill(3) + '</td>\n\t\t<td class="second">')
        user = User.query.filter_by(user_id=x).first()
        y = 'Not Found' if user is None else user.real_id
        results += (x + '</td>\n\t\t<td>' + y + '</td>\n\t</tr>\n')
    return render_template('results.html', results=results)
