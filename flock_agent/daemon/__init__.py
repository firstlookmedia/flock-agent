# -*- coding: utf-8 -*-
import asyncio
from .daemon import Daemon


def main(common):
    d = Daemon(common)

    # This requires python 3.7+
    # asyncio.run(d.start())

    # This works in python 3.6
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([d.start()]))


def stop(common):
    from ..gui.daemon_client import DaemonClient

    deamon_client = DaemonClient(common)
    deamon_client.shutdown()
