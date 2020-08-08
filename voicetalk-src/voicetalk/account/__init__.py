import logging

from voicetalk.config import config
from voicetalk.db import models
from voicetalk.db.db import DB
from voicetalk.utils import password

logger = logging.getLogger('VoiceTalk.account')


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
