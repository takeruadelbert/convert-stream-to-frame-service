import json
import os

import aiohttp
from aiohttp import FormData

from src.misc.constant.value import HTTP_STATUS_BAD_REQUEST

host_storage = "{}:{}".format(os.getenv("STORAGE_HOST"), os.getenv("STORAGE_PORT"))
url_upload_base64 = "{}/{}".format(host_storage, os.getenv("STORAGE_UPLOAD_BASE64_URL"))
url_upload_raw = "{}/{}".format(host_storage, os.getenv("STORAGE_UPLOAD_RAW_URL"))
url_upload_via_url = "{}/{}".format(host_storage, os.getenv("STORAGE_UPLOAD_VIA_URL"))

upload_types = {
    'raw': url_upload_raw,
    'base64': url_upload_base64,
    'url': url_upload_via_url
}


async def json_upload(**kwargs):
    upload_type = kwargs.get("upload_type", "raw")
    host = upload_types[upload_type]
    payload = kwargs.get("payload")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(host, json=payload) as response:
                return await handle_response(response)
    except Exception as err:
        return handle_error(err)


async def form_upload(**kwargs):
    host = upload_types['raw']
    payload = kwargs.get("payload")
    temp = payload['files']
    file = temp.file
    filename = temp.filename
    content_type = temp.content_type
    name = temp.name

    data = FormData()
    data.add_field(name, file, filename=filename, content_type=content_type)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(host, data=data) as response:
                return await handle_response(response)
    except Exception as err:
        return handle_error(err)


async def handle_response(response):
    temp = await response.text()
    data = json.loads(temp)
    return {
        'status': response.status,
        'message': data['message'],
        'token': data['data'][0]['token']
    }


def handle_error(err):
    print("error = ", err)
    return {
        'status': HTTP_STATUS_BAD_REQUEST,
        'message': err,
    }
