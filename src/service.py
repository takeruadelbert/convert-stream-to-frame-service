import base64
import os
import random

import cv2
from fastapi import HTTPException
from pydantic import ValidationError

from broker.broker import Broker
from database.database import Database
from misc.constant.message import *
from misc.constant.value import *
from misc.helper.helper import get_current_timestamp_ms
from storage.storage import json_upload


def return_message(**kwargs):
    message = kwargs.get("message", "")
    status = kwargs.get("status", HTTP_STATUS_OK)
    data = kwargs.get("data", [])
    if status != HTTP_STATUS_OK:
        raise HTTPException(status_code=status, detail=message)
    return {'message': message, 'data': data}


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

    async def upload_encoded(self, payload):
        try:
            self.logger.info('received data from master node : {}'.format(payload.filename))
            feedback_url = payload.feedback_url
            ticket_number = await self.upload_image_to_broker(feedback_url, upload_type='base64', payload=[payload.dict()])
            return self.show_ticket_number(ticket_number)
        except ValidationError as error:
            return self.process_error(error)
        except Exception as error:
            return self.process_error(error)

    async def upload_raw(self, payload):
        try:
            self.logger.info('received data from master node : {}'.format(payload))
            feedback_url = payload.feedback_url
            ticket_number = await self.upload_image_to_broker(feedback_url, upload_type='raw', payload=payload)
            return self.show_ticket_number(ticket_number)
        except Exception as error:
            return self.process_error(error)

    async def upload_url(self, payload):
        try:
            self.logger.info('received data from master node : {}'.format(payload))
            feedback_url = payload.feedback_url
            ticket_number = await self.upload_image_to_broker(feedback_url, upload_type='url', payload=payload.dict())
            return self.show_ticket_number(ticket_number)
        except ValidationError as error:
            return self.process_error(error)
        except Exception as error:
            return self.process_error(error)

    def show_ticket_number(self, ticket_number):
        if ticket_number:
            data = {'ticket_number': ticket_number}
            self.logger.info('{} : {}'.format(MESSAGE_SUCCESS_SENT_DATA_TO_QUEUE, data))
            return return_message(message=MESSAGE_SUCCESS_SENT_DATA_TO_QUEUE, data=data)
        else:
            self.logger.error(MESSAGE_INVALID_TICKET_NUMBER)
            return return_message(status=HTTP_STATUS_UNPROCESSABLE_ENTITY, message=MESSAGE_INVALID_TICKET_NUMBER)

    def process_error(self, error):
        message = "Error when processing received data from master node : {}".format(error)
        self.logger.error(message)
        return return_message(status=HTTP_STATUS_UNPROCESSABLE_ENTITY, message=message)

    async def upload_image_to_broker(self, feedback_url, **kwargs):
        upload_type = kwargs.get("upload_type")
        payload = kwargs.get("payload")
        if payload:
            response = json_upload(upload_type=upload_type, payload=payload)
            if response['status'] == HTTP_STATUS_OK:
                token = response['token']
                ticket_number = get_current_timestamp_ms()
                if self.database.add_default_image_result_data(ticket_number, token, feedback_url):
                    sent_payload = {'token': token, 'ticket_number': ticket_number}
                    self.logger.info('sending payload {} to queue'.format(sent_payload))
                    self.broker.produce(topic=os.getenv("KAFKA_IMAGE_PROCESS_TOPIC"), payload=sent_payload)
                    return ticket_number
                else:
                    return None
            else:
                self.logger.error(MESSAGE_UPLOAD_ERROR)
                return None
        else:
            self.logger.warning(MESSAGE_IMAGE_PAYLOAD_EMPTY)
            return None

    async def upload_send_to_broker(self, data, gate_id, stream):
        if data:
            for item in data:
                response_upload = json_upload(upload_type='base64', payload=[item])
                if response_upload['status'] == HTTP_STATUS_OK:
                    token = response_upload['token']
                    sent_payload = {
                        'gate_id': gate_id,
                        'token': token
                    }
                    self.logger.info('sending payload {} to queue.'.format(sent_payload))
                    self.broker.produce(topic=os.getenv("KAFKA_TOPIC"), payload=sent_payload)
                else:
                    self.logger.error(MESSAGE_UPLOAD_ERROR)
                    return return_message(status=HTTP_STATUS_BAD_REQUEST, message=MESSAGE_UPLOAD_ERROR)
        else:
            message = '{} [{}]'.format(MESSAGE_CANNOT_READ_STREAM, stream)
            self.logger.warning(message)
            return return_message(status=HTTP_STATUS_BAD_REQUEST, message=message)

    async def auto_convert(self):
        data = self.database.fetch_data_stream()
        result = []
        if data:
            for state in data:
                url_stream = state.url
                id_gate = state.id_gate
                result.append({
                    'id_gate': id_gate,
                    'url_stream': url_stream
                })
                data_payload_queue = self.convert_stream_to_frame(url_stream)
                await self.upload_send_to_broker(data_payload_queue, id_gate, url_stream)
