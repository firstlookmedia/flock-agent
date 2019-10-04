# -*- coding: utf-8 -*-
import os
import grp
import asyncio
import json
from aiohttp import web

from .global_settings import GlobalSettings
from .osquery import Osquery


class Daemon:
    def __init__(self, common):
        self.c = common
        self.c.log("Daemon", "__init__")

        self.global_settings = GlobalSettings(common)

        self.osquery = Osquery(common, self.global_settings)
        self.osquery.refresh_osqueryd()
        common.osquery = self.osquery

        # Prepare the unix socket path
        self.unix_socket_path = "/var/lib/flock-agent/socket"
        os.makedirs("/var/lib/flock-agent", exist_ok=True)
        if os.path.exists(self.unix_socket_path):
            os.remove(self.unix_socket_path)

        # The socket uid will be 0 (root), and the group will be the administrator group. In debian-like
        # distros it's the "sudo" group, and in fedora-like distros it's the "wheel" group.
        # Other distros? PRs are welcome :).
        if os.path.isfile("/usr/bin/apt"):
            groupinfo = grp.getgrnam("sudo")
            self.gid = groupinfo.gr_gid
        elif os.path.isfile("/usr/bin/dnf") or os.path.isfile("/usr/bin/yum"):
            groupinfo = grp.getgrnam("wheel")
            self.gid = groupinfo.gr_gid
        else:
            # Unknown, so make the group root
            self.gid = 0

    async def start(self):
        await asyncio.gather(self.submit_loop(), self.http_server())

    async def submit_loop(self):
        while True:
            if self.global_settings.get("use_server") and self.global_settings.get(
                "gateway_token"
            ):
                # Submit osquery logs
                self.c.log("Daemon", "submit_loop", "Submitting osquery logs")
                try:
                    self.osquery.submit_logs()
                except Exception as e:
                    exception_type = type(e).__name__
                    self.c.log(
                        "Daemon",
                        "submit_loop",
                        "Exception submitting logs: {}".format(exception_type),
                    )

            # Wait a minute
            await asyncio.sleep(60)

    async def http_server(self):
        self.c.log("Daemon", "http_server", "Starting http server")

        # GET /ping, to check if the daemon is running
        async def ping(request):
            self.c.log("Daemon", "http_server", "GET /ping")
            return web.json_response(True)

        app = web.Application()
        app.router.add_get("/ping", ping)

        loop = asyncio.get_event_loop()
        await loop.create_unix_server(app.make_handler(), self.unix_socket_path)

        # Change permissions of unix socket
        os.chmod(self.unix_socket_path, 0o660)
        os.chown(self.unix_socket_path, 0, self.gid)
