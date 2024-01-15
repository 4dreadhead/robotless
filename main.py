import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api import api_classes

load_dotenv()


def main():
    app = FastAPI()
    [api_class(app) for api_class in api_classes]

    uvicorn.run(
        app,
        host=os.getenv("API_HOST"),
        port=int(os.getenv("API_PORT")),
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTIFICATE")
    )


if __name__ == '__main__':
    main()
