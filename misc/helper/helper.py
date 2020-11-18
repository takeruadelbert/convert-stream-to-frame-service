import os
import time


def create_log_dir_if_does_not_exists(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def get_current_timestamp_ms():
    return int(round(time.time() * 1000))
