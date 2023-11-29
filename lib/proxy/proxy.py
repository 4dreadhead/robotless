import asyncio

import mitmproxy.addons.proxyserver

from proxy_mitmproxy import Mitmproxy


async def run_proxy():
    from mitmproxy.tools import dump
    from mitmproxy import options
    opts = options.Options(listen_host='127.0.0.0', listen_port=3000)
    s = dump.DumpMaster(opts)
    s.server = mitmproxy.addons.proxyserver.Proxyserver()
    s.addons.add(Mitmproxy(3000, 3030))
    await s.run()


if __name__ == '__main__':
    asyncio.run(run_proxy())
