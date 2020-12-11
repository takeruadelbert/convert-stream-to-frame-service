import os
import time

import arrow

from src.misc.constant.value import DEFAULT_DATETIME_FORMAT


def create_log_dir_if_does_not_exists(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def get_current_timestamp_ms():
    return int(round(time.time() * 1000))


def get_current_datetime():
    return arrow.now().format(DEFAULT_DATETIME_FORMAT)
