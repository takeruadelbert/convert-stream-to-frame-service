import os


def create_log_dir_if_does_not_exists(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
