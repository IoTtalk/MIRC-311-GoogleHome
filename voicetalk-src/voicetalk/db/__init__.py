import logging
import pkg_resources
import subprocess

from voicetalk.config import config

logger = logging.getLogger('VoiceTalk.db')


def create():
    alembic_directory = pkg_resources.resource_filename('voicetalk', 'alembic/alembic.ini')

    result = subprocess.run(
        ['alembic', '-c', alembic_directory,
            '-x', 'db_url={}'.format(config.db_conf['url']), 'upgrade', 'head'])

    if result.returncode == 0:
        logger.info('Database migration was successful')
    else:
        logger.error('Database migration failed')
