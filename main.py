import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler

from aiohttp import web
from aiojobs.aiohttp import setup

from misc.constant.value import DEFAULT_PORT, DEFAULT_APP_NAME
from misc.helper.helper import create_log_dir_if_does_not_exists
from service import ConvertStreamToFrameService

logger = logging.getLogger(DEFAULT_APP_NAME)


def setup_log():
    log_format = "%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s"
    log_level = logging.DEBUG
    handler = TimedRotatingFileHandler("log/{}.log".format(DEFAULT_APP_NAME), when="midnight", interval=1)
    handler.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    handler.suffix = "%Y%m%d"
    handler.extMatch = re.compile(r"^\d{8}$")
    logger.setLevel(log_level)
    logger.addHandler(handler)


create_log_dir_if_does_not_exists('log')
setup_log()
service = ConvertStreamToFrameService(logger)


def setup_route():
    return [
        web.post('/stream-to-frame', service.receive_from_master_node),
        web.get('/stream', service.fetch_data)
    ]


async def initialization():
    app = web.Application()
    app.router.add_routes(setup_route())
    setup(app)
    return app


if __name__ == "__main__":
    web.run_app(initialization(), port=os.getenv('PORT', DEFAULT_PORT))
