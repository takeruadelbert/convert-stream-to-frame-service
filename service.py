import os
import random

import cv2
from aiohttp import web

from misc.constant.message import INVALID_PAYLOAD_DATA_MESSAGE
from misc.constant.value import *


class ConvertStreamToFrameService:
    def __init__(self):
        pass

    def return_message(self, **kwargs):
        message = kwargs.get("message", "")
        status = kwargs.get("status", HTTP_STATUS_OK)
        return web.json_response({'message': message}, status=status)

    def convert_stream_to_frame(self, stream):
        result, frames = [], []
        capture = cv2.VideoCapture(stream)
        for index in range(DEFAULT_FPS):
            ret, frame = capture.read()
            frames.append(frame)
        capture.release()

        if frames:
            for index in range(os.getenv("NUMBER_OF_FRAME_TAKEN", DEFAULT_NUMBER_OF_FRAME_TAKEN)):
                selected_index_frame = random.randint(0, DEFAULT_FPS - 1)
                # encoded_frame = self.frame2base64(frames[selected_index_frame])
                result.append(frames[selected_index_frame])
        return result

    async def receive_from_master_node(self, request):
        payload = await request.json()
        if not payload['data']:
            return self.return_message(message=INVALID_PAYLOAD_DATA_MESSAGE, status=HTTP_STATUS_BAD_REQUEST)
        sent_payload = []
        for data in payload['data']:
            stream = data['url_stream']
            frames = self.convert_stream_to_frame(stream)
            sent_payload.append({
                'gate_id': data['gate_id'],
                'images': frames
            })
        return self.return_message(message=sent_payload)

    def upload_image_to_storage(self):
        return self.return_message(message='Success')
