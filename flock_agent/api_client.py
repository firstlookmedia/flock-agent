# -*- coding: utf-8 -*-
import requests
import base64
import json


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
        self.c.log("FlockApiClient", "__init__")

    def register(self):
        self.c.log("FlockApiClient", "register")

        obj = self._make_request('/register', 'post', False, {
            'username': self.c.settings.get('gateway_username')
        })

        if 'auth_token' not in obj:
            raise InvalidResponse()

        # If we made it this far, looks like we registered successfully
        # Save the token
        self.c.settings.set('gateway_token', obj['auth_token'])
        self.c.settings.save()

    def ping(self):
        self.c.log("FlockApiClient", "ping")

        obj = self._make_request('/ping', 'get', True)

    def _make_request(self, path, method, auth, data=None):
        url = self._build_url(path)
        if method == 'get':
            requests_func = requests.get
        elif method == 'post':
            requests_func = requests.post

        self.c.log("FlockApiClient", "_make_request", "{} {}".format(method, url))

        try:
            res = requests_func(url, data=data, headers=self._get_headers(auth))
            self.c.log("FlockApiClient", "_make_request", "status_code: {}, data: {}".format(res.status_code, res.content))
        except requests.exceptions.ConnectionError:
            raise ConnectionError()

        if res.status_code == 401:
            raise PermissionDenied()

        if res.content:
            try:
                obj = json.loads(res.content)
            except:
                raise ResponseIsNotJson()

            if obj['error']:
                if 'error_msg' in obj:
                    raise RespondedWithError(obj['error_msg'])
                else:
                    raise InvalidResponse()

            return obj

        if res.status_code != 200:
            raise BadStatusCode(res)

    def _build_url(self, path):
        """
        Build the URL of a request, with a path starting with "/"
        """
        return '{}{}'.format(self.c.settings.get('gateway_url').rstrip('/'), path)

    def _get_headers(self, auth):
        headers = {}
        headers['User-Agent'] = 'Flock Agent {}'.format(self.c.version)
        if auth:
            encoded_credentials = base64.b64encode('{}:{}'.format(self.c.settings.get('gateway_username'), self.c.settings.get('gateway_token')).encode()).decode()
            headers['Authorization'] = 'Basic {}'.format(encoded_credentials)
        return headers
