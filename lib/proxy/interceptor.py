import sys
import os
import json
import time
from mitmproxy import http
from mitmproxy import tls
from mitmproxy.connection import ConnectionState
from mitmproxy.proxy.server_hooks import ServerConnectionHookData
from mitmproxy.proxy import events
# from psutil import process_iter
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from lib.analyzers.tls.parser import TlsParser

load_dotenv()


class Mitmproxy:
    def __init__(self):
        self.proxy_destination_port = int(os.getenv("API_PORT"))
        self.proxy_destination_host = os.getenv("API_HOST")
        self.tls_client = {}
        self.clean_timeout = 60
        self.last_clean_time = time.time()

    def request(self, flow: http.HTTPFlow):
        flow.request.scheme = "https"
        flow.request.host = self.proxy_destination_host
        flow.request.port = self.proxy_destination_port
        flow.request.headers["Connection"] = "close"
        flow.request.headers["x-tls"] = self.tls_client.get(flow.client_conn.peername, "{}")

    def response(self, flow: http.HTTPFlow):
        flow.request.headers["Connection"] = "close"
        flow.response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        flow.response.headers["Pragma"] = "no-cache"

    def tls_clienthello(self, data: tls.ClientHelloData):
        current_time = time.time()
        if current_time - self.last_clean_time > self.clean_timeout:
            self.last_clean_time = current_time
            to_delete = []

            for key, value in self.tls_client.items():
                fp = json.loads(value)
                if time.time() - fp[TlsParser.TIMESTAMP_KEY] > self.clean_timeout:
                    to_delete.append(key)

            for key in to_delete:
                del self.tls_client[key]

        if not self.tls_client.get(data.context.client.peername):
            self.tls_client[data.context.client.peername] = TlsParser(data.client_hello.raw_bytes()).as_str()


addons = [Mitmproxy()]
