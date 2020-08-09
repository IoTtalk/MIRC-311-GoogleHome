import logging
import pkg_resources
import subprocess
import sys

from argparse import ArgumentParser

from voicetalk import version
from voicetalk import utils
from voicetalk.config import config


def main():
    parser, args = parse_args()

    load_config(args)
    logging.basicConfig(level=logging.INFO)

    if hasattr(args, 'func'):
        return getattr(args, 'func')(args)

    parser.print_help()


def parse_args():
    """Parse arguments
    """
    parser = ArgumentParser(description='VoiceTalk controller')
    subparsers = parser.add_subparsers(title='Available sub-commands')

    parser.add_argument(
        '-c', '--config',
        dest='ini_path',
        default=None,
        help='VoiceTalk ini config file'
    )

    parser.add_argument(
        '-f', '--device-json-file',
        dest='device_json_file_path',
        default=None,
        help='Device json file'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='VoiceTalk {}'.format(version)
    )

    # Sub command: ``start``
    msg = 'Start VoiceTalk server'
    start_command_parser = subparsers.add_parser('start', description=msg, help=msg)
    start_command_parser.set_defaults(func=start_voicetalk)

    # Sub command: ``db``
    msg = 'Database management'
    db_command_parser = subparsers.add_parser('db', description=msg, help=msg)
    db_command_subparsers = db_command_parser.add_subparsers(title='Available sub-commands')
    parse_db_subcommand(db_command_subparsers)

    # Sub command: ``add-user``
    msg = 'Add an user for Oauth2.0'
    add_user_command_parser = subparsers.add_parser('add-user', description=msg, help=msg)
    add_user_command_parser.add_argument('username', metavar='USERNAME', type=str,
                                         help='The username')
    add_user_command_parser.set_defaults(func=add_user)

    # Sub command: ``remove-user``
    msg = 'Remove an user for Oauth2.0'
    remove_user_command_parser = subparsers.add_parser('remove-user', description=msg,
                                                       help=msg)
    remove_user_command_parser.add_argument('username', metavar='USERNAME', type=str,
                                            help='The username')
    remove_user_command_parser.set_defaults(func=remove_user)

    # Sub command: ``genconf``
    msg = 'Generate the sample configuration file'
    genconf_command_parser = subparsers.add_parser('genconf', description=msg, help=msg)
    genconf_command_parser.add_argument('sample_conf_destination',
                                        metavar='DESTINATION',
                                        type=str,
                                        help='Destination of the sample configuration file')
    genconf_command_parser.set_defaults(func=handle_genconf)

    # Sub command: ``gen-sample-device-file``
    msg = 'Generate the sample device file in json format'
    gen_device_file_command_parser = subparsers.add_parser('gen-sample-device-file',
                                                           description=msg, help=msg)
    gen_device_file_command_parser.add_argument('sample_device_json_file_destination',
                                                metavar='DESTINATION',
                                                type=str,
                                                help='Destination of the'
                                                     'sample device json file')
    gen_device_file_command_parser.set_defaults(func=handle_gen_device_file)

    return parser, parser.parse_args()


def parse_db_subcommand(db_command_subparsers):
    msg = 'Create database for Oauth2'
    db_create_parser = db_command_subparsers.add_parser('create', description=msg, help=msg)
    db_create_parser.set_defaults(func=create_db)


def add_user(args):
    import getpass

    from voicetalk import account

    password = getpass.getpass(
        'Please enter the password for the user {}: '.format(getattr(args, 'username')))
    repeated_password = getpass.getpass(
        'Please re-enter the password for the user {}: '.format(getattr(args, 'username')))

    if password != repeated_password:
        print('Password does not match!!!')
        sys.exit(1)

    account.add_an_user(getattr(args, 'username'), password)


def remove_user(args):
    from voicetalk import account

    account.remove_an_user(getattr(args, 'username'))


def handle_genconf(args):
    sample_configuration_file_path = \
        pkg_resources.resource_filename('voicetalk', 'conf/voicetalk.ini.sample')
    utils.copy_sample_file(sample_configuration_file_path,
                           getattr(args, 'sample_conf_destination'),
                           'Sample configuration file does not exist')


def handle_gen_device_file(args):
    sample_device_json_file_path = \
        pkg_resources.resource_filename('voicetalk', 'device/device.json.sample')
    utils.copy_sample_file(sample_device_json_file_path,
                           getattr(args, 'sample_device_json_file_destination'),
                           'Sample device file does not exist')


def create_db(args):
    from voicetalk import db

    db.create()


def start_voicetalk(args):
    try:
        # Using this import statement to check whether it's in uwsgi or not
        import uwsgi  # noqa: F401
    except ModuleNotFoundError:
        subprocess.run(['uwsgi', '--http-socket',
                        '{}:{}'.format(config.bind_address, config.bind_port),
                        '--wsgi', 'voicetalk.wsgi',
                        '--pyargv', ' '.join(sys.argv[1:])])
    else:
        from voicetalk.server import app
        load_flask_config(app)

        return app


def load_config(args, config_file_arg_name: str = 'ini_path'):
    """Load configuration file specified in the command line options
    """
    if getattr(args, config_file_arg_name):
        config.read_config(getattr(args, config_file_arg_name))


def load_flask_config(app):
    app.secret_key = config.flask_secret_key


if __name__ == '__main__':
    main()
