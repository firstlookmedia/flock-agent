# -*- coding: utf-8 -*-
import asyncio
from .daemon import Daemon


def main(common):
    d = Daemon(common)
    asyncio.run(d.start())
