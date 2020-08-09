import itertools

from pathlib import Path
from setuptools import find_packages, setup

import voicetalk

BASE_DIR = str(Path(__file__).resolve().parent)


def get_requires():
    requirements_path = Path(BASE_DIR) / 'requirements.txt'
    with requirements_path.open() as f:
        return tuple(map(str.strip, f.readlines()))


def get_files(directory: str):
    """
    Get all the files in a given directory and return their paths in a list.

    The returned paths are relative to the directory that contains ``setup.py``.

    It currently ignores ``__pycache__`` directory.

    :param directory: Target directory
    :type directory: ``str``
    :return: A list of file names
    :rtype: ``list``
    """
    include_files = []

    for path in Path(directory).rglob('*'):
        if str(path).find('__pycache__') != -1:
            continue

        include_files.append(
            str(path.relative_to('{}/voicetalk'.format(BASE_DIR))))

    return include_files


def get_alembic_data():
    alembic_directory = Path(BASE_DIR) / 'voicetalk/alembic'

    return get_files(str(alembic_directory))


def get_template_files():
    templates_directory = Path(BASE_DIR) / 'voicetalk/templates'

    return get_files(str(templates_directory))


def get_static_files():
    static_files_directory = Path(BASE_DIR) / 'voicetalk/static'

    return get_files(str(static_files_directory))


setup(
    name='VoiceTalk',
    version=voicetalk.version,
    description='VoiceTalk for MIRC311',
    packages=find_packages(exclude=['tests']),
    package_data={
        'voicetalk': list(
            itertools.chain(
                get_alembic_data(),
                ['device/device.json.sample', 'conf/voicetalk.ini.sample'],
                get_template_files(),
                get_static_files()
            )
        )
    },
    zip_safe=True,
    entry_points={
        'console_scripts': ['voice-talk = voicetalk.cli:main'],
    },
    install_requires=get_requires(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ]
)
