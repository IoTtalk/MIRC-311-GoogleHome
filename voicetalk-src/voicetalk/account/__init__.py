import logging

from voicetalk.config import config
from voicetalk.db import models
from voicetalk.db.db import DB
from voicetalk.utils import password

logger = logging.getLogger('VoiceTalk.account')


def exist(db_session, username: str) -> bool:
    """
    Check a specific user exists or not.

    :param db_session: SQLAlchemy ORM session
    :param username: Username
    :type username: ``str``
    :return: ``True`` if the user exists, ``False`` otherwise.
    :rtype: bool
    """
    return get(db_session, username) is not None


def get(db_session, username: str) -> models.User or None:
    """
    Get the user whose username is the given username.

    :param db_session: SQLAlchemy ORM session
    :param username: Username
    :type username: ``str``
    :return: The mapped User object if the user exists, ``None`` otherwise.
    :rtype: voicetalk.db.models.User or None
    """
    return (db_session.query(models.User)
                      .filter_by(username=username)
                      .first())


def add_an_user(username: str, plaintext_password: str) -> models.User or None:
    db_instance = DB()
    db_instance.connect(config.db_conf['url'])

    if not username or not plaintext_password:
        return None

    try:
        hashed_password = password.hash(plaintext_password)
    except RuntimeError:
        return None

    user = models.User(username=username, password=hashed_password)

    with db_instance.get_session_scope() as session:
        session.add(user)

    logger.info('Add user {} successfully'.format(username))


def remove_an_user(username: str) -> None:
    db_instance = DB()
    db_instance.connect(config.db_conf['url'])

    if not username:
        return

    with db_instance.get_session_scope() as db_session:
        (db_session.query(models.User)
                   .filter_by(username=username)
                   .delete())

    logger.info('Delete user {} successfully'.format(username))
