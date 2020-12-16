import os
import sys

from py_eureka_client.eureka_client import EurekaClient

from src.misc.constant.value import APP_NAME, DEFAULT_PORT_EUREKA, DEFAULT_PORT

eureka_server = "{}:{}".format(os.getenv("EUREKA_HOST"), os.getenv("EUREKA_PORT", DEFAULT_PORT_EUREKA))
app_name = os.getenv("APP_NAME", APP_NAME)
app_port = int(os.getenv("PORT", DEFAULT_PORT))


def register_service_to_eureka_server(logger):
    try:
        client = EurekaClient(eureka_server=eureka_server, app_name=app_name, instance_port=app_port)
        client.start()
        register_success = "Register to Eureka server {} success.".format(eureka_server)
        print(register_success)
        logger.info(register_success)
    except Exception as error:
        register_error = "Failed to register service to Eureka Server : {}".format(error)
        print(register_error)
        logger.error(register_error)
        sys.exit()
