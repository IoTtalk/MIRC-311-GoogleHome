import logging
import multiprocessing

from argon2 import PasswordHasher
from argon2.exceptions import (HashingError, VerificationError, VerifyMismatchError,
                               InvalidHash)

logger = logging.getLogger('VoiceTalk.utils.password')
password_hasher = PasswordHasher(parallelism=2 * multiprocessing.cpu_count())


def hash(plaintext_password: str) -> str:
    """
    Hash the given plaintext password by argon2ID.

    :param plaintext_password: Plaintext password
    :type plaintext_password: ``str``
    :raise RuntimeError: If password hashing failed.
    :raise ValueError: If the ``plaintext_password`` is empty.
    :return: Hashed password on success,
        rasie `ValueError` or `RuntimeError` otherwise.
    :rtype: ``str``
    """
    if not plaintext_password:
        raise ValueError('Password can not be empty')

    try:
        return password_hasher.hash(plaintext_password)
    except HashingError:
        raise RuntimeError('Password hashing failed')


def verify(hashed_password: str, plaintext_password: str) -> bool:
    """
    Verify the given plaintext password is matched with the hashed password or not.

    :param hashed_password: Hashed password
    :type hashed_password: str
    :param plaintext_password: Plaintext password
    :type plaintext_password: str
    :return: ``True`` on success, raise ``RuntimeError`` otherwise.
    :rtype: ``bool``
    """
    try:
        return password_hasher.verify(hashed_password, plaintext_password)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        raise RuntimeError('Password verification failed')
