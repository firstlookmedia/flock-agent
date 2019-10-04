# -*- coding: utf-8 -*-
import json
import requests

# requests_unixsocket is included in this repo, because it's not packaged in fedora
from . import requests_unixsocket


class DaemonNotRunningException(Exception):
    pass


class PermissionDeniedException(Exception):
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
        """
        Ping the daemon, to see if we can connect and it's working
        """
        return self._get("/ping")

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

    def _get(self, path):
        url = "http+unix://{}{}".format(self.unix_socket_path.replace("/", "%2F"), path)
        self.c.log("DaemonClient", "_get", "GET {}".format(url))

        try:
            r = self.session.get(url)
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
                return False

        if r.status_code == 200:
            obj = json.loads(r.text)
            return obj
        return False
