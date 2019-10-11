# -*- coding: utf-8 -*-
import asyncio
from .daemon import Daemon


def main(common):
    d = Daemon(common)
    asyncio.run(d.start())


def stop(common):
    from ..gui.daemon_client import DaemonClient

    deamon_client = DaemonClient(common)
    deamon_client.shutdown()
