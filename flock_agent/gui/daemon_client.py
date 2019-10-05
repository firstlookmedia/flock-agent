# -*- coding: utf-8 -*-
import json
import requests

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
        self.unix_socket_path = "/var/lib/flock-agent/socket"

    def ping(self):
        self._http_get("/ping")

    def get(self, key):
        res = self._http_get("/setting/{}".format(key))
        return res["data"]

    def set(self, key, val):
        res = self._http_post("/setting/{}".format(key), val)
        return res["data"]

    def enable_twig(self, twig_id):
        res = self._http_post("/enable_twig", twig_id)
        return res["data"]

    def disable_twig(self, twig_id):
        res = self._http_post("/disable_twig", twig_id)
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

    def refresh_osqueryd(self):
        res = self._http_get("/refresh_osqueryd")
        return res["data"]

    def register_server(self, server_url, name):
        pass
        """
        # Validate server URL
        o = urlparse(server_url)
        if (
            (o.scheme != "http" and o.scheme != "https")
            or (o.path != "" and o.path != "/")
            or o.params != ""
            or o.query != ""
            or o.fragment != ""
        ):

            Alert(self.c, "Invalid server URL").launch()
            return False

        # Save the server URL in settings
        self.c.settings.set("gateway_url", server_url)
        self.c.settings.save()

        # Try to register
        self.c.log('SettingsTab', 'server_button_clicked', 'registering with server')
        api_client = FlockApiClient(self.c)
        try:
            api_client.register(name)
            api_client.ping()
            return True
        except PermissionDenied:
            Alert(self.c, 'Permission denied').launch()
        except BadStatusCode as e:
            Alert(self.c, 'Bad status code: {}'.format(e)).launch()
        except ResponseIsNotJson:
            Alert(self.c, 'Server response is not JSON').launch()
        except RespondedWithError as e:
            Alert(self.c, 'Server error: {}'.format(e)).launch()
        except InvalidResponse:
            Alert(self.c, 'Server returned an invalid response').launch()
        except ConnectionError:
            Alert(self.c, 'Error connecting to server').launch()
        return False
        """

    def _http_get(self, path):
        return self._http_request("get", path)

    def _http_post(self, path, data=None):
        return self._http_request("post", path, data)

    def _http_request(self, method, path, data=None):
        url = "http+unix://{}{}".format(self.unix_socket_path.replace("/", "%2F"), path)
        if data:
            self.c.log(
                "DaemonClient", "_request", "{} {} {}".format(method, path, data)
            )
        else:
            self.c.log("DaemonClient", "_request", "{} {}".format(method, path))

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
                self.c.log("DaemonClient", "_request", "Error: {}".format(obj["error"]))
            return obj

        raise UnknownErrorException
