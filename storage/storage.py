import json
import os

import requests

from misc.constant.value import HTTP_STATUS_BAD_REQUEST

url = "{}:{}/{}".format(os.getenv("STORAGE_HOST"), os.getenv("STORAGE_PORT"), os.getenv("STORAGE_UPLOAD_URL"))


def upload(payload):
    try:
        response = requests.post(url, json=payload)
        data = json.loads(response.text)
        return {
            'status': response.status_code,
            'message': data['message'],
            'token': data['data'][0]['token']
        }
    except Exception as err:
        print("error = ", err)
        return {
            'status': HTTP_STATUS_BAD_REQUEST,
            'message': err,
        }
