import logging
import urllib

from datetime import datetime, timedelta

from flask import (Flask, jsonify, render_template, request, redirect,
                   make_response)
from flask_login import (current_user, login_required, login_user, logout_user,
                         LoginManager)

from voicetalk import const as CONST
from voicetalk import device
from voicetalk import cli
from voicetalk.config import config
from voicetalk.db import models
from voicetalk.db.db import DB
from voicetalk.iottalk import DAN
from voicetalk.oauth2 import oauth2
from voicetalk.utils import get_one_hour_after_timestamp, get_random_token, password

app = Flask(__name__)
dan_instance = DAN.DAN()
login_manager = LoginManager()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VoiceTalk')

# Parse the command line arguments
parser, args = cli.parse_args()

# Load the configuration
cli.load_config(args)

iottalk_profile = {
    'd_name': config.iottalk_conf['device_name'],
    'dm_name': config.iottalk_conf['device_model_name'],
    'df_list': [config.iottalk_conf['device_feature']],
    'is_sim': False
}

login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    db_instance = DB()
    with db_instance.get_session_scope() as db_session:
        user = (db_session.query(models.User)
                .filter_by(id=id)
                          .first())
        # Expunge the user instance so it can be accessed after the session is committed
        db_session.expunge(user)

    return user


@app.before_first_request
def f():
    db_instance = DB()
    db_instance.connect(config.db_conf['url'])


@app.route('/fulfillment', methods=['POST'])
def fulfillment():
    authorization_header = request.headers.get('Authorization')
    db_instance = DB()

    if not authorization_header:
        return '', 401

    # Validate the access token
    try:
        access_token = authorization_header.split(' ')[1]
    except IndexError:
        access_token = None

    with db_instance.get_session_scope() as db_session:
        access_token_instance = (db_session.query(models.AccessToken)
                                           .filter_by(token=access_token)
                                           .first())
        if not oauth2.validate_access_token(access_token_instance):
            return '', 401

        u_id = access_token_instance.u_id

    request_payload = request.get_json()

    if not request_payload:
        return jsonify({}), 200

    inputs = request_payload.get('inputs', [])
    request_id = request_payload.get('requestId')
    response_payload = {}
    response = {'requestId': request_id, 'payload': response_payload}

    for input_data in inputs:
        logger.info('{} request'.format(input_data['intent']))
        req_response_payload = {}
        if input_data['intent'] == 'action.devices.SYNC':
            logger.info('SYNC intent')
            req_response_payload = \
                {
                    'devices': device.get_device_data(
                        getattr(args, 'device_json_file_path')),
                    'agentUserId': u_id
                }
        elif input_data['intent'] == 'action.devices.EXECUTE':
            logger.info('EXECUTE intent')
            dan_instance.push(config.iottalk_conf['device_feature'], input_data)
            req_response_payload = \
                {
                    'commands': device.handle_execute_intent(
                        input_data['payload'].get('commands', [[]]))
                }
        elif input_data['intent'] == 'action.devices.QUERY':
            logger.info('QUERY intent')
            '''
            Currently, this intent is not available.
            Use 'actionNotAvailable' ERROR to response
            '''
            req_response_payload = \
                {
                    'devices': device.hanlde_query_intent(
                        input_data['payload'].get('devices', []))
                }
        elif input_data['intent'] == 'action.devices.DISCONNECT':
            logger.info('DISCONNECT intent')
            # Google Smarthome is unlinking, deregister the corresponding DA on the IoTtalk
            dan_instance.deregister()

        response_payload.update(req_response_payload)

    return make_response(jsonify(response), 200)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_instance = DB()
    redirect_uri = request.args.get('redirect_uri')
    client_id = request.args.get('client_id')
    response_type = request.args.get('response_type')
    state = request.args.get('state')
    user_locale = request.args.get('user_locale')

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        if not request.form.get('username') or not request.form.get('password'):
            return render_template(
                'login.html',
                error_msg='Both of username and password should not be empty')

        username = request.form.get('username')
        plaintext_password = request.form.get('password')

        with db_instance.get_session_scope() as db_session:
            user = (db_session.query(models.User)
                              .filter_by(username=username)
                              .first())

            if not user:
                return render_template(
                    'login.html',
                    error_msg='Account does not exist!')

            try:
                password.verify(user.password, plaintext_password)
            except RuntimeError:
                return render_template('login.html',
                                       error_msg='Wrong username or password.')

            login_user(user)

        if not redirect_uri:
            redirect_uri = '/'
        else:
            redirect_uri = '/oauth' \
                           '?redirect_uri={}' \
                           '&client_id={}' \
                           '&response_type={}' \
                           '&state={}' \
                           '&user_locale={}'.format(
                               redirect_uri,
                               client_id,
                               response_type,
                               state,
                               user_locale)

        return redirect(redirect_uri)


@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect('/')


@app.route('/oauth')
def oauth():
    db_instance = DB()
    authorization_code = request.args.get('authorization_code')
    redirect_uri = request.args.get('redirect_uri')
    client_id = request.args.get('client_id')
    response_type = request.args.get('response_type')
    state = request.args.get('state')
    user_locale = request.args.get('user_locale')

    if response_type != 'code':
        return make_response('response_type must be \'code\'', 500)

    if client_id != config.google_conf.get('client_id'):
        return make_response('Invalid client_id: {}'.format(client_id), 500)

    # Redirect the user to the login page if he/she is not logged in yet
    if not current_user.is_authenticated:
        logger.warn('Current user is not logged in yet.')
        redirect_location = \
            '/login' \
            '?redirect_uri={}' \
            '&client_id={}' \
            '&response_type={}' \
            '&state={}' \
            '&user_locale={}'.format(
                redirect_uri,
                client_id,
                response_type,
                state,
                user_locale
            )
        return redirect(redirect_location)

    logger.info('User is authenticated')

    authorization_code = get_random_token(48)
    authorization_code_instance = models.AuthorizationCode(
        code=authorization_code,
        expires_at=(datetime.now() + timedelta(minutes=10)).timestamp(),
        redirect_uri=redirect_uri)

    with db_instance.get_session_scope() as db_session:
        # Add the current user to the session since it has been detached
        db_session.add(current_user)
        current_user.authorization_codes.append(authorization_code_instance)

    return redirect('{}?code={}&state={}'.format(urllib.parse.unquote(redirect_uri),
                                                 authorization_code,
                                                 state))


@app.route('/token', methods=['POST'])
def token():
    db_instance = DB()
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    code = request.form.get('code')
    grant_type = request.form.get('grant_type')
    redirect_uri = request.form.get('redirect_uri')
    refresh_token = request.form.get('refresh_token')

    # Check the existence of the client ID and the client secret
    if not client_id or not client_secret:
        logger.warn('Receive a token request, but it misses required payload')
        return make_response(jsonify(CONST.INVALID_GRANT_RESPONSE), 400)

    # Validate the client ID and the client secret
    if client_id != config.google_conf['client_id'] or \
       client_secret != config.google_conf['client_secret']:
        logger.warn('Receive a token request, but it is an unmatched client')
        return make_response(jsonify(CONST.INVALID_GRANT_RESPONSE), 400)

    if grant_type == 'authorization_code':
        with db_instance.get_session_scope() as db_session:
            authorization_code_instance = (db_session.query(models.AuthorizationCode)
                                                     .filter_by(code=code)
                                                     .first())
            # Validate the authorization code
            if not oauth2.validate_authorization_code(authorization_code_instance,
                                                      urllib.parse.unquote(redirect_uri)):
                # Delete the invalid authorization code
                if not authorization_code_instance:
                    db_session.delete(authorization_code_instance)
                logger.warn(
                    'Receive a token request,'
                    'but it contains an invalid authorization code')
                return make_response(jsonify(CONST.INVALID_GRANT_RESPONSE), 400)

            access_token = get_random_token(64)
            refresh_token = get_random_token(64)

            # Make sure no repeated tokens
            while True:
                if not oauth2.access_token_exists(db_session, access_token):
                    break
            while True:
                if not oauth2.refresh_token_exists(db_session, refresh_token):
                    break

            access_token_instance = models.AccessToken(
                token=access_token,
                expires_at=get_one_hour_after_timestamp(),
                u_id=authorization_code_instance.u_id)
            refresh_token_instance = models.RefreshToken(
                token=refresh_token,
                u_id=authorization_code_instance.u_id)
            refresh_token_instance.access_token = access_token_instance

            db_session.add(access_token_instance)
            db_session.add(refresh_token_instance)
            db_session.delete(authorization_code_instance)

            response_object = {
                'token_type': 'Bearer',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': 3600
            }

            # Register on the IoTtalk
            dan_instance.device_registration_with_retry(iottalk_profile,
                                                        config.iottalk_conf['host'])

            return jsonify(response_object)
    elif grant_type == 'refresh_token':
        with db_instance.get_session_scope() as db_session:
            refresh_token_instance = (db_session.query(models.RefreshToken)
                                                .filter_by(token=refresh_token)
                                                .first())
            if not refresh_token_instance:
                return make_response(jsonify(CONST.INVALID_GRANT_RESPONSE), 400)

            # Update the access token
            new_access_token = get_random_token(64)
            refresh_token_instance.access_token.token = new_access_token
            refresh_token_instance.access_token.expires_at = get_one_hour_after_timestamp()
            response_object = {
                'token_type': 'Bearer',
                'access_token': new_access_token,
                'expires_in': 3600
            }

            return jsonify(response_object)
    else:
        logger.warn(
            'Receive a token request,'
            'but it contains an unsupported grant type {}'.format(grant_type))
        return make_response(jsonify(CONST.INVALID_GRANT_RESPONSE), 400)


@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)


def main():
    app.run(host=config.bind_address,
            port=config.bind_port,
            debug=False)


if __name__ == '__main__':
    main()
