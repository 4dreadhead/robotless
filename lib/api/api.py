import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
import ssl

from . import api_classes


def run_api():
    load_dotenv()

    host = os.getenv("API_HOST")
    port = int(os.getenv("API_PORT"))

    api = FastAPI()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    initialized_apis = [api_class(api) for api_class in api_classes]

    uvicorn.run(
        api,
        host=host,
        port=port,
        ssl_keyfile='/home/zhdanov/PycharmProjects/robotless/mycert.key',
        ssl_certfile='/home/zhdanov/PycharmProjects/robotless/mycert.crt'
    )
