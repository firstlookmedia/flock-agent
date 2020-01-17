# -*- coding: utf-8 -*-
import json
import logging
import requests

from .gui_common import Alert
from ..common import Platform

# requests_unixsocket is included in this repo, because it's not packaged in fedora
from . import requests_unixsocket


class DaemonNotRunningException(Exception):
    pass


class PermissionDeniedException(Exception):
    pass


class UnknownErrorException(Exception):
    pass


class DaemonClient:
    """
    The client that communicates with the daemon's server
    """

    def __init__(self, common):
        self.c = common

        self.session = requests_unixsocket.Session()
        if Platform.current() == Platform.MACOS:
            self.unix_socket_path = "/usr/local/var/lib/flock-agent/socket"
        else:
            self.unix_socket_path = "/var/lib/flock-agent/socket"

    def ping(self):
        self._http_get("/ping")

    def shutdown(self):
        """
        Stop the background daemon
        """
        try:
            self._http_post("/shutdown")
        except:
            pass

    def get(self, key):
        res = self._http_get("/setting/{}".format(key))
        return res["data"]

    def set(self, key, val):
        res = self._http_post("/setting/{}".format(key), val)
        return res["data"]

    def exec_twig(self, twig_id):
        res = self._http_get("/exec_twig/{}".format(twig_id))
        return res["data"]

    def enable_undecided_twigs(self):
        res = self._http_post("/enable_undecided_twigs")
        return res["data"]

    def get_decided_twig_ids(self):
        res = self._http_get("/decided_twig_ids")
        return res["data"]

    def get_undecided_twig_ids(self):
        res = self._http_get("/undecided_twig_ids")
        return res["data"]

    def get_enabled_twig_ids(self):
        res = self._http_get("/enabled_twig_ids")
        return res["data"]

    def get_twig_enabled_statuses(self):
        res = self._http_get("/twig_enabled_statuses")
        return res["data"]

    def update_twig_status(self, twig_status):
        res = self._http_post("/update_twig_status", twig_status)
        return res["data"]

    def exec_health(self, health_item_name):
        res = self._http_get("/exec_health/{}".format(health_item_name))
        return res["data"]

    def register_server(self, server_url, name):
        res = self._http_post(
            "/register_server", {"server_url": server_url, "name": name}
        )
        if res["error"]:
            Alert(self.c, res["error"]).launch()
            return False
        else:
            return True

    def _http_get(self, path):
        return self._http_request("get", path)

    def _http_post(self, path, data=None):
        return self._http_request("post", path, data)

    def _http_request(self, method, path, data=None):
        logger = logging.getLogger("DaemonClient._http_request")
        url = "http+unix://{}{}".format(self.unix_socket_path.replace("/", "%2F"), path)
        if data:
            logger.info(f"{method} {path} {data}")
        else:
            logger.info(f"{method} {path}")

        try:
            if method == "get":
                r = self.session.get(url)
            else:
                r = self.session.post(url, json=data)
        except requests.exceptions.ConnectionError as e:
            exception_type = type(e.args[0].args[1])
            if (
                exception_type == FileNotFoundError
                or exception_type == ConnectionRefusedError
            ):
                raise DaemonNotRunningException
            elif exception_type == PermissionError:
                raise PermissionDeniedException
            else:
                raise UnknownErrorException

        if r.status_code == 200:
            obj = json.loads(r.text)
            if obj["error"]:
                logger.info(f"Error: {obj['error']}'")
            return obj

        raise UnknownErrorException
