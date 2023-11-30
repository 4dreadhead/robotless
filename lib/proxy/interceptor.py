import sys
import os
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

    def request(self, flow: http.HTTPFlow):
        flow.request.scheme = "https"
        flow.request.host = self.proxy_destination_host
        flow.request.port = self.proxy_destination_port

        flow.request.headers["tls"] = self.tls_client.get(flow.client_conn.peername, "{}")

    def tls_clienthello(self, data: tls.ClientHelloData):
        try:
            result = TlsParser(data.client_hello.raw_bytes()).as_str()
        except Exception as error:
            result = '{"error": "%s"}' % error

        self.tls_client[data.context.client.peername] = result


addons = [Mitmproxy()]
