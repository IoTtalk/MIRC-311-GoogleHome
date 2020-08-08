import secrets
import shutil

from datetime import datetime, timedelta
from pathlib import Path


def copy_sample_file(sample_file_path: str, sample_file_destination: str,
                     error_msg: str = 'Sample file does not exist') -> None:
    """Copy the sample file to the specified destination.

    If the sample file does not exist or the destination is empty, it
    raise ``OSError`` exception.

    :param sample_file_path: Sample file path.
    :type sample_file_path: str
    :param sample_file_destination: Sample file destination.
    :type sample_file_destination: str
    :error_msg: Error msg when sample file does not exist.
      Defaults to ``Sample file does not exist``
    :type error_msg: str
    :rtype: None
    """
    if not Path(sample_file_path).exists():
        raise OSError(error_msg)

    if not sample_file_destination:
        raise OSError('Destination is None')

    shutil.copy(sample_file_path, sample_file_destination)


def get_ten_minutes_after_timestamp() -> int:
    """Get the timestamp of the time ten minutes from now.

    :return: The timestamp of the time ten minutes from now.
    :rtype: int
    """
    return (datetime.now() + timedelta(minutes=10)).timestamp()


def get_one_hour_after_timestamp() -> int:
    """Get the timestamp of the time one hour from now.

    :return: The timestamp of the time one hour from now.
    :rtype: int
    """
    return (datetime.now() + timedelta(hours=1)).timestamp()


def get_random_token(length: int = 48) -> str:
    """Get a random url-safe token

    :param length: Length of the token in bytes. Defaults to 48.
    :return: A random token in bytes type
    :rtype: bytes
    """
    return secrets.token_urlsafe(length)
