import json
import os

import py_eureka_client.eureka_client as eureka_client

from src.misc.constant.value import HTTP_STATUS_BAD_REQUEST, LPR_STORAGE_APP_NAME, RETURN_TYPE_JSON, \
    HTTP_REQUEST_METHOD_POST

url_upload_base64 = os.getenv("STORAGE_UPLOAD_BASE64_URL")
url_upload_raw = os.getenv("STORAGE_UPLOAD_RAW_URL")
url_upload_via_url = os.getenv("STORAGE_UPLOAD_VIA_URL")

upload_types = {
    'raw': url_upload_raw,
    'base64': url_upload_base64,
    'url': url_upload_via_url
}


def json_upload(**kwargs):
    upload_type = kwargs.get("upload_type", "raw")
    url_path = upload_types[upload_type]
    payload = kwargs.get("payload")
    payload = json.dumps(payload).encode()
    try:
        header = {
            "Content-Type": "application/json"
        }
        response = eureka_client.do_service(LPR_STORAGE_APP_NAME, url_path, method=HTTP_REQUEST_METHOD_POST,
                                            headers=header, data=payload, return_type=RETURN_TYPE_JSON)
        return handle_response(response)
    except Exception as err:
        return handle_error(err)


def handle_response(response):
    return {
        'status': response['status'],
        'message': response['message'],
        'token': response['data'][0]['token']
    }


def handle_error(err):
    print("error = ", err)
    return {
        'status': HTTP_STATUS_BAD_REQUEST,
        'message': err,
    }
