from aiohttp import web

from misc.constant.message import INVALID_PAYLOAD_DATA_MESSAGE
from misc.constant.value import HTTP_STATUS_OK, HTTP_STATUS_NO_CONTENT


class ConvertStreamToFrameService:
    def __init__(self):
        pass

    async def receive_from_master_node(self, request):
        payload = await request.json()
        if not payload['data']:
            return self.return_message(message=INVALID_PAYLOAD_DATA_MESSAGE, status=HTTP_STATUS_NO_CONTENT)
        return self.return_message(message=payload)

    def return_message(self, **kwargs):
        message = kwargs.get("message", "")
        status = kwargs.get("status", HTTP_STATUS_OK)
        return web.json_response({'message': message}, status=status)
