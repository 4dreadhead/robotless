import sys
import os
import json
import time
from mitmproxy import http
from mitmproxy import tls
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

        flow.request.headers["tls"] = self.tls_client.get(flow.client_conn.peername, "{}")

    def tls_clienthello(self, data: tls.ClientHelloData):
        if time.time() - self.last_clean_time > self.clean_timeout:
            self.last_clean_time = time.time()

            for key, value in self.tls_client.items():
                fp = json.loads(value)
                if time.time() - fp[TlsParser.TIMESTAMP_KEY] > self.clean_timeout:
                    del self.tls_client[key]

        if not self.tls_client.get(data.context.client.peername):
            self.tls_client[data.context.client.peername] = TlsParser(data.client_hello.raw_bytes()).as_str()


addons = [Mitmproxy()]
