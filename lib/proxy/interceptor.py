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
        self.tls_client = {}

    def request(self, flow: http.HTTPFlow):
        flow.request.scheme = "https"
        flow.request.host = "127.0.0.1"
        flow.request.port = self.proxy_destination_port

        flow.request.headers["tls"] = self.tls_client.get(flow.client_conn.peername, "{}")

    def tls_clienthello(self, data: tls.ClientHelloData):
        try:
            result = TlsParser(data.client_hello.raw_bytes()).as_str()
        except Exception as error:
            result = '{"error": "%s"}' % error

        self.tls_client[data.context.client.peername] = result

    def response(self, flow: http.HTTPFlow):
        try:
            del self.tls_client[flow.client_conn.peername]
        except KeyError:
            pass


addons = [Mitmproxy()]
