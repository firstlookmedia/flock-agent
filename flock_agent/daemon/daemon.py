# -*- coding: utf-8 -*-
import os
import sys
import grp
import asyncio
import json
import time
from urllib.parse import urlparse
from aiohttp import web
from aiohttp.abc import AbstractAccessLogger
from aiohttp.web_runner import GracefulExit

from .global_settings import GlobalSettings
from .osquery import Osquery
from .flock_logs import FlockLog, FlockLogTypes
from .api_client import (
    FlockApiClient,
    PermissionDenied,
    BadStatusCode,
    ResponseIsNotJson,
    RespondedWithError,
    InvalidResponse,
    ConnectionError,
)
from ..common import Platform
from ..health import health_items


class Daemon:
    def __init__(self, common):
        self.c = common

        # Daemon's log
        if Platform.current() == Platform.MACOS:
            log_dir = "/usr/local/var/log/flock-agent"
        else:
            log_dir = "/var/log/flock-agent"
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, "log")
        self.c.log_filename = log_filename

        self.c.log("Daemon", "__init__")

        self.osquery = Osquery(common)
        self.c.osquery = self.osquery

        self.global_settings = GlobalSettings(common)
        self.c.global_settings = self.global_settings

        self.api_client = FlockApiClient(self.c)

        # Flock Agent lib directory
        if Platform.current() == Platform.MACOS:
            lib_dir = "/usr/local/var/lib/flock-agent"
        else:
            lib_dir = "/var/lib/flock-agent"
        os.makedirs(lib_dir, exist_ok=True)

        # Flock Agent keeps its own submission queue separate from osqueryd, for when users
        # enable/disable the server, or enable/disable twigs
        self.flock_log = FlockLog(self.c, lib_dir)

        # Prepare the unix socket path
        self.unix_socket_path = os.path.join(lib_dir, "socket")
        if os.path.exists(self.unix_socket_path):
            os.remove(self.unix_socket_path)

        # The socket uid will be 0 (root), and the group will be the administrator group.
        # In macOS, this group is "admin". In debian-like distros it's "sudo", and in fedora-like
        # distros it's the "wheel" group. Other distros? PRs are welcome :).
        if Platform.current() == Platform.MACOS:
            groupinfo = grp.getgrnam("admin")
            self.gid = groupinfo.gr_gid
        else:
            if os.path.isfile("/usr/bin/apt"):
                groupinfo = grp.getgrnam("sudo")
                self.gid = groupinfo.gr_gid
            elif os.path.isfile("/usr/bin/dnf") or os.path.isfile("/usr/bin/yum"):
                groupinfo = grp.getgrnam("wheel")
                self.gid = groupinfo.gr_gid
            else:
                # Unknown, so make the group root
                self.gid = 0

        # Start with refreshing osqueryd
        self.osquery.refresh_osqueryd()

    async def start(self):
        await asyncio.gather(self.submit_loop(), self.http_server())

    async def submit_loop(self):
        while True:
            if self.global_settings.get("use_server") and self.global_settings.get(
                "gateway_token"
            ):
                # Submit osquery logs
                try:
                    self.osquery.submit_logs()
                except Exception as e:
                    exception_type = type(e).__name__
                    self.c.log(
                        "Daemon",
                        "submit_loop",
                        "Exception submitting logs: {}".format(exception_type),
                    )

                # Submit Flock Agent logs
                self.flock_log.submit_logs()

            # Wait a minute
            await asyncio.sleep(60)

    async def http_server(self):
        self.c.log("Daemon", "http_server", "Starting http server")

        def response_object(data=None, error=False):
            obj = {"data": data, "error": error}
            return web.json_response(obj)

        # Access logs
        common_log = self.c.log

        class AccessLogger(AbstractAccessLogger):
            def log(self, request, response, time):
                common_log(
                    "Daemon.http_server",
                    "AccessLogger",
                    "{} {} {}".format(request.method, request.path, response.status),
                )

        # Routes
        async def ping(request):
            return response_object()

        async def shutdown(request):
            self.c.log("Daemon", "http_server", "GET /shutdown, shutting down daemon")
            raise GracefulExit()

        async def get_setting(request):
            key = request.match_info.get("key", None)
            try:
                return response_object(self.global_settings.get(key))
            except:
                return response_object(error="invalid key")

        async def set_setting(request):
            key = request.match_info.get("key", None)
            val = await request.json()

            # Only change the setting if it's actually changing
            old_val = self.global_settings.get(key)
            if old_val == val:
                self.c.log(
                    "Daemon",
                    "http_server.set_settings",
                    "skipping {}={}, because it's already set".format(key, val),
                )
            else:
                self.c.log(
                    "Daemon",
                    "http_server.set_settings",
                    "setting {}={}".format(key, val),
                )
                self.global_settings.set(key, val)
                self.global_settings.save()

                if key == "use_server":
                    if val:
                        self.flock_log.log(FlockLogTypes.SERVER_ENABLED)
                    else:
                        self.flock_log.log(FlockLogTypes.SERVER_DISABLED)

            return response_object()

        async def get_twig(request):
            twig_id = request.match_info.get("twig_id", None)
            try:
                return response_object(self.global_settings.get_twig(twig_id))
            except:
                return response_object(error="invalid twig_id")

        async def exec_twig(request):
            twig_id = request.match_info.get("twig_id", None)
            try:
                twig = self.global_settings.get_twig(twig_id)
                data = self.osquery.exec(twig["query"])
                return response_object(data)
            except:
                return response_object(error="invalid twig_id")

        async def enable_undecided_twigs(request):
            enabled_twig_ids = []
            twig_ids = self.global_settings.get_undecided_twig_ids()
            for twig_id in twig_ids:
                if not self.global_settings.is_twig_enabled(twig_id):
                    self.global_settings.enable_twig(twig_id)
                    enabled_twig_ids.append(twig_id)

            if len(enabled_twig_ids) > 0:
                self.c.log(
                    "Daemon",
                    "http_server.enable_undecided_twigs",
                    "enabled twigs: {}".format(enabled_twig_ids),
                )
                self.global_settings.save()
                self.osquery.refresh_osqueryd()
                self.flock_log.log(FlockLogTypes.TWIGS_ENABLED, enabled_twig_ids)

            return response_object()

        async def get_decided_twig_ids(request):
            return response_object(self.global_settings.get_decided_twig_ids())

        async def get_undecided_twig_ids(request):
            return response_object(self.global_settings.get_undecided_twig_ids())

        async def get_enabled_twig_ids(request):
            return response_object(self.global_settings.get_enabled_twig_ids())

        async def update_twig_status(request):
            twig_status = await request.json()

            # Validate twig_status
            if type(twig_status) != dict:
                return response_object(error="twig_status must be a dict")
            for twig_id in twig_status:
                if twig_id not in self.global_settings.settings["twigs"]:
                    return response_object(
                        error="twig_status contains invalid twig_ids"
                    )
                if type(twig_status[twig_id]) != bool:
                    return response_object(error="twig_status is in an invalid format")

            enabled_twig_ids = []
            disabled_twig_ids = []

            for twig_id in twig_status:
                if twig_status[twig_id] and not self.global_settings.is_twig_enabled(
                    twig_id
                ):
                    self.global_settings.enable_twig(twig_id)
                    enabled_twig_ids.append(twig_id)
                if not twig_status[twig_id] and self.global_settings.is_twig_enabled(
                    twig_id
                ):
                    self.global_settings.disable_twig(twig_id)
                    disabled_twig_ids.append(twig_id)

            if len(enabled_twig_ids) > 0 or len(disabled_twig_ids) > 0:
                self.global_settings.save()
                self.osquery.refresh_osqueryd()

            if len(enabled_twig_ids) > 0:
                self.c.log(
                    "Daemon",
                    "http_server.update_twig_status",
                    "enabled twigs: {}".format(enabled_twig_ids),
                )
                self.flock_log.log(FlockLogTypes.TWIGS_ENABLED, enabled_twig_ids)
            if len(disabled_twig_ids) > 0:
                self.c.log(
                    "Daemon",
                    "http_server.update_twig_status",
                    "disabled twigs: {}".format(disabled_twig_ids),
                )
                self.flock_log.log(FlockLogTypes.TWIGS_DISABLED, disabled_twig_ids)

            return response_object()

        async def exec_health(request):
            health_item_name = request.match_info.get("health_item_name", None)
            query = None
            for health_item in health_items[Platform.current()]:
                if health_item["name"] == health_item_name:
                    query = health_item["query"]
                    break
            if query:
                try:
                    data = self.osquery.exec(query)
                    return response_object(data)
                except:
                    return response_object(error="error executing health item query")
            else:
                return response_object(error="invalid health_item_name")

        async def refresh_osqueryd(request):
            self.osquery.refresh_osqueryd()
            return response_object()

        async def register_server(request):
            data = await request.json()
            try:
                name = data["name"]
                server_url = data["server_url"]
            except:
                return response_object(error="Invalid request to daemon")

            # Validate server URL
            o = urlparse(server_url)
            if (
                (o.scheme != "http" and o.scheme != "https")
                or (o.path != "" and o.path != "/")
                or o.params != ""
                or o.query != ""
                or o.fragment != ""
            ):
                return response_object(error="Invalid server URL")

            # Save the server URL in settings
            self.global_settings.set("gateway_url", server_url)
            self.global_settings.save()

            # Try to register
            try:
                self.api_client.register(name)
                self.api_client.ping()
                return response_object()
            except PermissionDenied:
                return response_object(error="Permission denied")
            except BadStatusCode as e:
                return response_object(error="Bad status code: {}".format(e))
            except ResponseIsNotJson:
                return response_object(error="Server response is not JSON")
            except RespondedWithError as e:
                return response_object(error="Server error: {}".format(e))
            except InvalidResponse:
                return response_object(error="Server returned an invalid response")
            except ConnectionError:
                return response_object(error="Error connecting to server")

            # Anything else was an unknown failure
            return response_object(error="Unknown error")

        app = web.Application()
        app.router.add_get("/ping", ping)
        app.router.add_post("/shutdown", shutdown)
        app.router.add_get("/setting/{key}", get_setting)
        app.router.add_post("/setting/{key}", set_setting)
        app.router.add_get("/twig/{twig_id}", get_twig)
        app.router.add_get("/exec_twig/{twig_id}", exec_twig)
        app.router.add_post("/enable_undecided_twigs", enable_undecided_twigs)
        app.router.add_get("/decided_twig_ids", get_decided_twig_ids)
        app.router.add_get("/undecided_twig_ids", get_undecided_twig_ids)
        app.router.add_get("/enabled_twig_ids", get_enabled_twig_ids)
        app.router.add_post("/update_twig_status", update_twig_status)
        app.router.add_get("/exec_health/{health_item_name}", exec_health)
        app.router.add_get("/refresh_osqueryd", refresh_osqueryd)
        app.router.add_post("/register_server", register_server)

        loop = asyncio.get_event_loop()
        await loop.create_unix_server(
            app.make_handler(access_log_class=AccessLogger), self.unix_socket_path
        )

        # Change permissions of unix socket
        os.chmod(self.unix_socket_path, 0o660)
        os.chown(self.unix_socket_path, 0, self.gid)
