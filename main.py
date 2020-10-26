import os

from aiohttp import web
from aiojobs.aiohttp import setup

from misc.constant.value import DEFAULT_PORT
from service import ConvertStreamToFrameService

service = ConvertStreamToFrameService()


def setup_route():
    return [
        web.post('/stream-to-frame', service.receive_from_master_node),
    ]


async def initialization():
    app = web.Application()
    app.router.add_routes(setup_route())
    setup(app)
    return app


if __name__ == "__main__":
    web.run_app(initialization(), port=os.getenv('PORT', DEFAULT_PORT))
