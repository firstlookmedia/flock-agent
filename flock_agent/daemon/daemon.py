# -*- coding: utf-8 -*-
import asyncio
from .global_settings import GlobalSettings
from .osquery import Osquery


class Daemon:
    def __init__(self, common):
        self.c = common
        self.c.log("Daemon", "__init__")

        self.osquery = Osquery(common)
        common.osquery = self.osquery

        self.global_settings = GlobalSettings(common)

    async def start(self):
        while True:
            # Submit osquery logs
            self.c.log("Daemon", "start", "Submitting osquery logs")
            try:
                self.osquery.submit_logs()
            except Exception as e:
                exception_type = type(e).__name__
                self.c.log("Daemon", "start", "Exception submitting logs: {}".format(exception_type))

            # Wait a minute
            await asyncio.sleep(60)
