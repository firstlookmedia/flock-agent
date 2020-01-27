# -*- coding: utf-8 -*-
import base64
import logging
import requests


class PermissionDenied(Exception):
    """
    The API responded with a permission denied error
    """

    pass


class BadStatusCode(Exception):
    """
    The API responded with a non-200 status code
    """

    pass


class ResponseIsNotJson(Exception):
    """
    If the API response is not JSON
    """

    pass


class RespondedWithError(Exception):
    """
    If the API responded with an error message
    """

    pass


class InvalidResponse(Exception):
    """
    The API response didn't have the expected fields
    """

    pass


class ConnectionError(Exception):
    """
    Error connecting to API URL
    """

    pass


class FlockApiClient(object):
    """
    This is a client that interacts with the Flock gateway
    """

    def __init__(self, common):
        self.c = common
        logger = logging.getLogger("FlockApiClient.__init__")
        logger.debug("")

    def register(self, name):
        logger = logging.getLogger("FlockApiClient.register")
        logger.debug("")

        obj = self._make_request(
            "/register",
            "post",
            False,
            {"username": self.c.global_settings.get("gateway_username"), "name": name},
        )

        if "auth_token" not in obj:
            raise InvalidResponse()

        # If we made it this far, looks like we registered successfully
        # Save the token
        self.c.global_settings.set("gateway_token", obj["auth_token"])
        self.c.global_settings.save()

    def ping(self):
        logger = logging.getLogger("FlockApiClient.ping")
        logger.debug("")
        self._make_request("/ping", "get", True)

    def submit(self, data):
        """
        Submit data to the Flock server
        """
        logger = logging.getLogger("FlockApiClient.submit")
        logger.debug("")
        self._make_request("/submit", "post", True, data)

    def submit_flock_logs(self, data):
        """
        Submit flock logs to the Flock server
        """
        logger = logging.getLogger("FlockApiClient.submit_flock_logs")
        logger.debug("")
        self._make_request("/submit_flock_logs", "post", True, data)

    def _make_request(self, path, method, auth, data=None):
        """
        Makes a request to the api.

        path: uri path to which to make a request (string)
        method: the http method to use (string)
        auth: whether to use http authentication. (bool)
        data: Data to send with the reuqest (dict)
        """
        url = self._build_url(path)

        logger = logging.getLogger("FlockApiClient._make_request")
        logger.debug(f"{method} {url}")

        try:
            res = requests.request(
                method, url, json=data, headers=self._get_headers(auth)
            )

            logger.debug(f"status_code: {res.status_code}, data: {res.content}")

        except requests.exceptions.ConnectionError:
            raise ConnectionError()

        if res.status_code == 401:
            raise PermissionDenied()

        if res.status_code == 400:
            try:
                obj = res.json()
            except ValueError:
                raise ResponseIsNotJson()

            if obj["error"]:
                if "error_msg" in obj:
                    raise RespondedWithError(obj["error_msg"])
                else:
                    raise InvalidResponse()

        if res.status_code != 200:
            raise BadStatusCode(res)

        if res.content:
            try:
                obj = res.json()
            except ValueError:
                raise ResponseIsNotJson()
            return obj

    def _build_url(self, path):
        """
        Build the URL of a request, with a path starting with "/"
        """
        return "{}{}".format(
            self.c.global_settings.get("gateway_url").rstrip("/"), path
        )

    def _get_headers(self, auth):
        headers = {}
        headers["User-Agent"] = "Flock Agent {}".format(self.c.version)
        if auth:
            encoded_credentials = base64.b64encode(
                "{}:{}".format(
                    self.c.global_settings.get("gateway_username"),
                    self.c.global_settings.get("gateway_token"),
                ).encode()
            ).decode()
            headers["Authorization"] = "Basic {}".format(encoded_credentials)
        return headers
