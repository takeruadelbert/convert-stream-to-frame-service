import base64
import os
import random

import cv2
from aiohttp import web

from broker.broker import Broker
from misc.constant.message import *
from misc.constant.value import *
from storage.storage import upload


class ConvertStreamToFrameService:
    def __init__(self):
        self.broker = Broker()

    def return_message(self, **kwargs):
        message = kwargs.get("message", "")
        status = kwargs.get("status", HTTP_STATUS_OK)
        return web.json_response({'message': message}, status=status)

    def convert_stream_to_frame(self, stream):
        result, frames = [], []
        capture = cv2.VideoCapture(stream)
        for index in range(DEFAULT_FPS):
            ret, frame = capture.read()
            ret, buffer = cv2.imencode('.jpg', frame)
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

    async def receive_from_master_node(self, request):
        payload = await request.json()
        if not payload['data']:
            return self.return_message(message=INVALID_PAYLOAD_DATA_MESSAGE, status=HTTP_STATUS_BAD_REQUEST)
        for data in payload['data']:
            stream = data['url_stream']
            gate_id = data['gate_id']
            data_payload_queue = self.convert_stream_to_frame(stream)
            for item in data_payload_queue:
                response_upload = upload([item])
                if response_upload['status'] == HTTP_STATUS_OK:
                    sent_payload = {
                        'gate_id': gate_id,
                        'token': response_upload['token']
                    }
                    self.broker.produce(payload=sent_payload)
        return self.return_message(message=MESSAGE_SUCCESS_SENT_DATA_TO_QUEUE)
