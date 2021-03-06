import asyncio
import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler

import uvicorn
from fastapi import FastAPI

from src.eureka.eureka import register_service_to_eureka_server
from src.misc.constant.value import DEFAULT_PORT, DEFAULT_APP_NAME, DEFAULT_DELAY_TIME_CONVERT_STREAM_TO_FRAME_SCHEDULER
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
register_service_to_eureka_server(logger)
service = ConvertStreamToFrameService(logger)
app = FastAPI()


@app.post("/upload-encoded")
async def upload_encoded(encodedUpload: EncodedUpload):
    return await service.upload_encoded(encodedUpload)


@app.post("/upload-url")
async def upload_url(urlUpload: UrlUpload):
    return await service.upload_url(urlUpload)


@app.on_event("startup")
async def startup():
    asyncio.ensure_future(scheduler_convert_stream_to_frame())


async def scheduler_convert_stream_to_frame():
    logger.info('starting scheduler convert stream to frame ...')
    while True:
        await service.auto_convert()
        await asyncio.sleep(
            int(os.getenv("DELAY_TIME_CONVERT_STREAM_TO_FRAME_SCHEDULER",
                          DEFAULT_DELAY_TIME_CONVERT_STREAM_TO_FRAME_SCHEDULER)))


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv('PORT', DEFAULT_PORT)), host='0.0.0.0')
