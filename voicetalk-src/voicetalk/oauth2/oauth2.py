from datetime import datetime

from voicetalk.db import models

__all__ = ['access_token_exists', 'refresh_token_exists']


def access_token_exists(db_session, access_token: str) -> bool:
    """Check the given access token exists or not

    :param db_session: SQLAlchemy session
    :param access_token: Access token
    :type access_token: str
    :return: True or False
    :rtype: bool
    """
    return _token_exists(db_session, models.AccessToken, access_token, 'token')


def refresh_token_exists(db_session, refresh_token: str) -> bool:
    """Check the given refresh token exists or not

    :param db_session: SQLAlchemy session
    :param refresh_token: Refresh token
    :type refresh_token: str
    :return: True or False
    :rtype: bool
    """
    return _token_exists(db_session, models.RefreshToken, refresh_token, 'token')


def validate_access_token(access_token_instance: models.AccessToken) -> bool:
    """Validate the given access token

    :param access_token_instance: Access token instance
    :return: True or False.
      True means the given access token is valid.
      and is valid
    :rtype: bool
    """
    if not access_token_instance:
        return False
    elif datetime.now().timestamp() > access_token_instance.expires_at:
        return False
    else:
        return True


def validate_authorization_code(authorization_code_instance: models.AuthorizationCode,
                                redirect_uri: str) -> bool:
    """Validate the given authorization code

    :param authorization_code_instance
    :return: True or False.
      True means the given authorization code is valid.
    :rtype: bool
    """
    if not authorization_code_instance:
        return False
    elif datetime.now().timestamp() > authorization_code_instance.expires_at or \
            redirect_uri != authorization_code_instance.redirect_uri:
        return False
    else:
        return True


def _token_exists(db_session, model, token: str, column_name: str) -> bool:
    """Check the given token exists in the given table(model) or not

    :param db_session: SQLAlchemy session
    :param model: The mapped class
    :param token: token
    :type token: str
    :param column_name: The column representing as token
    :type column_name: str
    :return: True or False
    :rtype: bool
    """
    return (db_session.query(model)
            .filter_by(**{column_name: token})
            .first()) is not None
