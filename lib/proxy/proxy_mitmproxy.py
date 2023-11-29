from mitmproxy import http
from mitmproxy import tls
import sys
import os
from json import dumps

sys.path.append(os.getcwd())

from lib.analyzers.tls.parser import TlsParser


class Mitmproxy:
    def __init__(self, proxy_port, proxy_destination_port):
        self.proxy_port = proxy_port
        self.proxy_destination_port = proxy_destination_port
        self.tls_client = {}

    def request(self, flow: http.HTTPFlow):
        flow.request.scheme = "https"
        flow.request.port = self.proxy_destination_port

        flow.request.headers["tls"] = self.tls_client.get(flow.client_conn.peername, "{}")

    def tls_clienthello(self, data: tls.ClientHelloData):
        try:
            result = TlsParser(data.client_hello.raw_bytes()).as_str()
        except Exception as error:
            result = '{"error": "%s"}'

        self.tls_client[data.context.client.peername] = result

addons = [Mitmproxy(3000, 3030)]
