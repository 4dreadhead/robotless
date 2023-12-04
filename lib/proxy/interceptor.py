import os
import base64
from mitmproxy import http
from mitmproxy import tls
from dotenv import load_dotenv
load_dotenv()


class Mitmproxy:
    def __init__(self):
        self.proxy_destination_port = int(os.getenv("API_PORT"))
        self.proxy_destination_host = os.getenv("API_HOST")
        self.tls_of_clients = {}

    def request(self, flow: http.HTTPFlow):
        flow.request.scheme = "https"
        flow.request.host = self.proxy_destination_host
        flow.request.port = self.proxy_destination_port
        flow.request.headers["Connection"] = "close"
        flow.request.headers["X-Client-Hello"] = self.tls_of_clients.get(flow.client_conn.peername, "{}")

    def tls_clienthello(self, data: tls.ClientHelloData):
        key = data.context.client.peername
        if not self.tls_of_clients.get(key):
            self.tls_of_clients[key] = base64.b64encode(data.client_hello.raw_bytes()).decode("ascii")


addons = [Mitmproxy()]
