import json
import os
import aiohttp
import requests

from misc.constant.value import HTTP_STATUS_BAD_REQUEST

url = "{}:{}/{}".format(os.getenv("STORAGE_HOST"), os.getenv("STORAGE_PORT"), os.getenv("STORAGE_UPLOAD_URL"))


async def upload(payload):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                temp = await response.text()
                data = json.loads(temp)
                return {
                    'status': response.status,
                    'message': data['message'],
                    'token': data['data'][0]['token']
                }
    except Exception as err:
        print("error = ", err)
        return {
            'status': HTTP_STATUS_BAD_REQUEST,
            'message': err,
        }
