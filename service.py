import base64
import os
import random

import cv2
from aiohttp import web

from broker.broker import Broker
from database.database import Database
from misc.constant.message import *
from misc.constant.value import *
from storage.storage import upload


def return_message(**kwargs):
    message = kwargs.get("message", "")
    status = kwargs.get("status", HTTP_STATUS_OK)
    return web.json_response({'message': message}, status=status)


class ConvertStreamToFrameService:
    def __init__(self, logger):
        self.broker = Broker(logger)
        self.logger = logger
        self.database = Database(logger)

    def convert_stream_to_frame(self, stream):
        try:
            self.logger.info('converting stream {}'.format(stream))
            result, frames = [], []
            capture = cv2.VideoCapture(stream)
            for index in range(DEFAULT_FPS):
                ret, frame = capture.read()
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),
                                int(os.getenv("JPG_IMAGE_QUALITY", DEFAULT_JPG_IMAGE_QUALITY))]
                ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                encoded_image = base64.b64encode(buffer)
                frames.append(encoded_image.decode('utf-8'))
            capture.release()

            if frames:
                for index in range(int(os.getenv("NUMBER_OF_FRAME_TAKEN", DEFAULT_NUMBER_OF_FRAME_TAKEN))):
                    selected_index_frame = random.randint(0, DEFAULT_FPS - 1)
                    result.append({
                        'filename': "frame{}.jpg".format(selected_index_frame),
                        'encoded_file': "{}{}".format(DEFAULT_PREFIX_BASE64, frames[selected_index_frame])
                    })
            return result
        except Exception as error:
            self.logger.error('Cannot Converting Stream to Frame : {}'.format(error))
            return None

    async def receive_from_master_node(self, request):
        payload = await request.json()
        self.logger.info('received data from master node : {}'.format(payload))
        if not payload['data']:
            self.logger.warning(INVALID_PAYLOAD_DATA_MESSAGE)
            return return_message(message=INVALID_PAYLOAD_DATA_MESSAGE, status=HTTP_STATUS_BAD_REQUEST)
        for data in payload['data']:
            stream = data['url_stream']
            gate_id = data['gate_id']
            data_payload_queue = self.convert_stream_to_frame(stream)
            await self.upload_send_to_broker(data_payload_queue, gate_id, stream)

        self.logger.info(MESSAGE_SUCCESS_SENT_DATA_TO_QUEUE)
        return return_message(message=MESSAGE_SUCCESS_SENT_DATA_TO_QUEUE)

    async def upload_send_to_broker(self, data, gate_id, stream):
        if data:
            for item in data:
                response_upload = await upload([item])
                if response_upload['status'] == HTTP_STATUS_OK:
                    sent_payload = {
                        'gate_id': gate_id,
                        'token': response_upload['token']
                    }
                    self.logger.info('sending payload {} to queue.'.format(sent_payload))
                    self.broker.produce(payload=sent_payload)
                else:
                    self.logger.error(MESSAGE_UPLOAD_ERROR)
                    return return_message(status=HTTP_STATUS_BAD_REQUEST, message=MESSAGE_UPLOAD_ERROR)
        else:
            return return_message(status=HTTP_STATUS_BAD_REQUEST,
                                  message='{} [{}]'.format(MESSAGE_CANNOT_READ_STREAM, stream))

    async def auto_convert(self):
        data = self.database.fetch_data_stream()
        result = []
        if data:
            for state in data:
                url_stream = state[0]
                gate_id = state[1]
                result.append({
                    'gate_id': gate_id,
                    'url_stream': url_stream
                })
                data_payload_queue = self.convert_stream_to_frame(url_stream)
                await self.upload_send_to_broker(data_payload_queue, gate_id, url_stream)
