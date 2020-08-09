import logging

from configparser import ConfigParser
from pathlib import Path

logger = logging.getLogger('VoiceTalk.config')


class Config:
    __bind_address = '0.0.0.0'
    __bind_port = 443
    __flask_secret_key = 'FLASK_SECRET_KEY'
    __username = ''
    __password = ''
    __db_conf = {
        'url': 'DB_URL',
        'pool_recycle': 600
    }
    __google_conf = {
        'client_id': 'CLIENT_ID',
        'client_secret': 'CLIENT_SECRET',
        'api_key': 'API_KEY'
    }
    __iottalk_conf = {
        'host': 'http://iottalk.tw:9999',
        'device_name': '311_GoogleHome',
        'device_model_name': 'GoogleHome',
        'device_feature': 'Voice-I'
    }

    def read_config(self, path: str):
        if not path or not Path(path).is_file():
            raise OSError('ini file not found: {}'.format(path))

        config = ConfigParser()
        config.read(path)

        def set_(obj, attribute: str, config: dict, data_type=str, option=None,
                 parse_func=None):
            def get_option_value_from_config():
                option_value = data_type(config.get(option, default_value))

                if parse_func:
                    return parse_func(option_value)
                else:
                    return option_value

            if option is None:
                option = attribute

            try:
                if isinstance(obj, dict):
                    default_value = obj.get(attribute)
                    obj[attribute] = get_option_value_from_config()
                else:
                    default_value = getattr(obj, attribute)
                    setattr(obj, attribute, get_option_value_from_config())
            except(AttributeError, ValueError):
                logger.warning('Skip unknown config: {}'.format(option))

        if config.has_section('core'):
            s = dict(config.items('core'))
            set_(self, 'bind_address', s, option='bind')
            set_(self, 'bind_port', s, int, 'port')
            set_(self, 'flask_secret_key', s)
            set_(self, 'username', s)
            set_(self, 'password', s)

        if config.has_section('db'):
            s = dict(config.items('db'))
            set_(self.__db_conf, 'url', s)
            set_(self.__db_conf, 'pool_recycle', s, data_type=int, option='pool-recycle')

        if config.has_section('google-api'):
            s = dict(config.items('google-api'))
            set_(self.__google_conf, 'client_id', s)
            set_(self.__google_conf, 'client_secret', s)
            set_(self.__google_conf, 'api_key', s)

        if config.has_section('iottalk'):
            s = dict(config.items('iottalk'))
            set_(self.__iottalk_conf, 'host', s)
            set_(self.__iottalk_conf, 'device_name', s)
            set_(self.__iottalk_conf, 'device_model_name', s)
            set_(self.__iottalk_conf, 'device_feature', s)

    @property
    def bind_address(self):
        return self.__bind_address

    @bind_address.setter
    def bind_address(self, bind_address: str):
        if not isinstance(bind_address, str):
            return

        self.__bind_address = bind_address

    @property
    def bind_port(self):
        return self.__bind_port

    @bind_port.setter
    def bind_port(self, port: int):
        self.__bind_port = self.__parse_port(port)

    @property
    def flask_secret_key(self):
        return self.__flask_secret_key

    @flask_secret_key.setter
    def flask_secret_key(self, flask_secret_key):
        self.__flask_secret_key = flask_secret_key

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username: str):
        self.__username = username

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password: str):
        self.__password = password

    @property
    def db_conf(self):
        return self.__db_conf

    @property
    def google_conf(self):
        return self.__google_conf

    @property
    def iottalk_conf(self):
        return self.__iottalk_conf

    def __parse_port(self, port: int) -> int:
        port = int(port)

        if port < 0 or port > 65535:
            raise ValueError('Port must be in between 0 to 65535')
        else:
            return port


config = Config()
