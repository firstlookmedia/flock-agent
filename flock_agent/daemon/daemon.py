# -*- coding: utf-8 -*-
import os
import sys
import grp
import asyncio
import json
import time
import requests
import subprocess
from urllib.parse import urlparse
from packaging.version import parse as parse_version
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

        self.c.log("Daemon", "__init__", f"version {self.c.version}")

        self.osquery = Osquery(common)
        self.c.osquery = self.osquery

        hostname = self.osquery.exec("SELECT uuid AS host_uuid FROM system_info;")
        if hostname:
            hostname = hostname[0]["host_uuid"]

        self.global_settings = GlobalSettings(common, hostname)
        self.c.global_settings = self.global_settings

        self.api_client = FlockApiClient(self.c)

        # Flock Agent lib directory
        if Platform.current() == Platform.MACOS:
            self.lib_dir = "/usr/local/var/lib/flock-agent"
        else:
            self.lib_dir = "/var/lib/flock-agent"
        os.makedirs(self.lib_dir, exist_ok=True)

        # Flock Agent keeps its own submission queue separate from osqueryd, for when users
        # enable/disable the server, or enable/disable twigs
        self.flock_log = FlockLog(self.c, self.lib_dir)

        # Prepare the unix socket path
        self.unix_socket_path = os.path.join(self.lib_dir, "socket")
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
        await asyncio.gather(
            self.submit_loop(), self.http_server(), self.autoupdate_loop()
        )

    async def submit_loop(self):
        while True:
            if self.global_settings.get("use_server") and self.global_settings.get(
                "gateway_token"
            ):
                await self.submit_logs_osquery()
                await self.submit_logs_flock()

            # Wait a minute
            await asyncio.sleep(60)

    async def submit_logs_osquery(self):
        # Submit osquery logs
        try:
            self.osquery.submit_logs()
        except Exception as e:
            exception_type = type(e).__name__
            self.c.log(
                "Daemon", "submit_loop", f"Exception submitting logs: {exception_type}"
            )

    async def submit_logs_flock(self):
        # Submit Flock Agent logs
        try:
            self.flock_log.submit_logs()
        except Exception as e:
            exception_type = type(e).__name__
            self.c.log(
                "Daemon",
                "submit_loop",
                f"Exception submitting flock logs: {exception_type}",
            )

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
                    f"{request.method} {request.path} {response.status}",
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
                    f"skipping {key}={val}, because it's already set",
                )
            else:
                self.c.log("Daemon", "http_server.set_settings", f"setting {key}={val}")
                self.global_settings.set(key, val)
                self.global_settings.save()

                if key == "use_server":
                    if val:
                        self.flock_log.log(FlockLogTypes.SERVER_ENABLED)
                    else:
                        self.flock_log.log(FlockLogTypes.SERVER_DISABLED)
                        # Submit flock logs right away
                        await self.submit_logs_flock()

            return response_object()

        async def exec_twig(request):
            twig_id = request.match_info.get("twig_id", None)
            try:
                twig = self.global_settings.get_twig(twig_id)
                data = self.osquery.exec(twig["query"])
                return response_object(data)
            except:
                return response_object(error="invalid twig_id")

        async def enable_undecided_twigs(request):
            # If the user choose to automatically opt-in to new twigs, this enables them all
            enabled_twig_ids = []
            twig_ids = self.global_settings.get_undecided_twig_ids()
            for twig_id in twig_ids:
                if not self.global_settings.is_twig_enabled(twig_id):
                    self.global_settings.enable_twig(twig_id)
                    enabled_twig_ids.append(twig_id)

            if enabled_twig_ids:
                self.c.log(
                    "Daemon",
                    "http_server.enable_undecided_twigs",
                    f"enabled twigs: {enabled_twig_ids}",
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

        async def get_twig_enabled_statuses(request):
            return response_object(self.global_settings.get_twig_enabled_statuses())

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
                if not twig_status[twig_id] and (
                    self.global_settings.is_twig_enabled(twig_id)
                    or self.global_settings.is_twig_undecided(twig_id)
                ):
                    self.global_settings.disable_twig(twig_id)
                    disabled_twig_ids.append(twig_id)

            if enabled_twig_ids or disabled_twig_ids:
                self.global_settings.save()
                self.osquery.refresh_osqueryd()

            if enabled_twig_ids:
                self.c.log(
                    "Daemon",
                    "http_server.update_twig_status",
                    f"enabled twigs: {enabled_twig_ids}",
                )
                self.flock_log.log(FlockLogTypes.TWIGS_ENABLED, enabled_twig_ids)
            if disabled_twig_ids:
                self.c.log(
                    "Daemon",
                    "http_server.update_twig_status",
                    f"disabled twigs: {disabled_twig_ids}",
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
                return response_object(error=f"Bad status code: {e}")
            except ResponseIsNotJson:
                return response_object(error="Server response is not JSON")
            except RespondedWithError as e:
                return response_object(error=f"Server error: {e}")
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
        app.router.add_get("/exec_twig/{twig_id}", exec_twig)
        app.router.add_post("/enable_undecided_twigs", enable_undecided_twigs)
        app.router.add_get("/decided_twig_ids", get_decided_twig_ids)
        app.router.add_get("/undecided_twig_ids", get_undecided_twig_ids)
        app.router.add_get("/enabled_twig_ids", get_enabled_twig_ids)
        app.router.add_get("/twig_enabled_statuses", get_twig_enabled_statuses)
        app.router.add_post("/update_twig_status", update_twig_status)
        app.router.add_get("/exec_health/{health_item_name}", exec_health)
        app.router.add_post("/register_server", register_server)

        loop = asyncio.get_event_loop()
        await loop.create_unix_server(
            app.make_handler(access_log_class=AccessLogger), self.unix_socket_path
        )

        # Change permissions of unix socket
        os.chmod(self.unix_socket_path, 0o660)
        os.chown(self.unix_socket_path, 0, self.gid)

    async def autoupdate_loop(self):
        # Autoupdate is only available for macOS right now; Linux uses package managers
        if Platform.current() != Platform.MACOS:
            return

        update_check_delay = 43200  # 12 hours

        while True:
            self.c.log("Daemon", "autoupdate_loop", "Checking for updates")

            try:
                # Query github for the latest version of Flock Agent
                r = requests.get(
                    "https://api.github.com/repos/firstlookmedia/flock-agent/releases/latest"
                )
                release = r.json()
                latest_version = release["tag_name"].lstrip("v")
                self.c.log(
                    "Daemon",
                    "autoupdate_loop",
                    f"installed version: {self.c.version}, latest version: {latest_version}",
                )
                if parse_version(latest_version) <= parse_version(self.c.version):
                    await asyncio.sleep(update_check_delay)
                    continue

                # Find the pkg asset
                url = None
                filename = None
                for asset in release["assets"]:
                    if asset["name"].endswith(".pkg"):
                        url = asset["browser_download_url"]
                        filename = asset["name"]
                        break

                if not url:
                    self.c.log("Daemon", "autoupdate_loop", "could not find .pkg file")
                    await asyncio.sleep(update_check_delay)
                    continue

                # Download the update
                self.c.log("Daemon", "autoupdate_loop", f"downloading {url}")
                r = requests.get(url)

                os.makedirs(os.path.join(self.lib_dir, "updates"), exist_ok=True)
                download_filename = os.path.join(self.lib_dir, "updates", filename)
                with open(download_filename, "wb") as f:
                    f.write(r.content)

                self.c.log(
                    "Daemon",
                    "autoupdate_loop",
                    f"download complete: {download_filename}",
                )

                # Verify that it's codesigned
                p = subprocess.run(
                    ["/usr/sbin/pkgutil", "--check-signature", download_filename],
                    stdout=subprocess.PIPE,
                )
                if (
                    p.returncode != 0
                    or (
                        # macOS 10.15
                        "Status: signed by a developer certificate issued by Apple for distribution"
                        not in p.stdout.decode()
                        # macOS 10.14
                        and "Status: signed by a certificate trusted by Mac OS X"
                        not in p.stdout.decode()
                    )
                    or "Developer ID Installer: FIRST LOOK PRODUCTIONS, INC. ("
                    not in p.stdout.decode()
                ):
                    self.c.log(
                        "Daemon",
                        "autoupdate_loop",
                        f"codesign verification failed: {p.stdout.decode()}",
                    )
                    await asyncio.sleep(update_check_delay)
                    continue

                # Install the update
                self.c.log(
                    "Daemon",
                    "autoupdate_loop",
                    "launching installer background process and quitting daemon",
                )
                subprocess.Popen(
                    ["/usr/sbin/installer", "-pkg", download_filename, "-target", "/"]
                )
                sys.exit(0)

            except Exception as e:
                self.c.log(
                    "Daemon",
                    "autoupdate_loop",
                    f"Exception while checking for updates: {e}",
                )
