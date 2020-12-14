import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler

import uvicorn
from fastapi import FastAPI

from src.misc.constant.value import DEFAULT_PORT, DEFAULT_APP_NAME
from src.misc.helper.helper import create_log_dir_if_does_not_exists
from src.model.model import EncodedUpload, UrlUpload
from src.service import ConvertStreamToFrameService

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
app = FastAPI()


@app.post("/upload-encoded")
async def upload_encoded(encodedUpload: EncodedUpload):
    return await service.upload_encoded(encodedUpload)


@app.post("/upload-url")
async def upload_url(urlUpload: UrlUpload):
    return await service.upload_url(urlUpload)


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv('PORT', DEFAULT_PORT)))
