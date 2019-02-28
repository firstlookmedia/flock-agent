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


class FlockApiClient(object):
    """
    This is a client that interacts with the Flock gateway
    """
    def __init__(self, common):
        self.c = common
        self.c.log("FlockApiClient", "__init__")

    def register(self):
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
        obj = self._make_request('/ping', 'get', True)

    def _make_request(self, path, method, auth, data=None):
        url = self._build_url(path)
        if method == 'get':
            request_func = request.get
        elif method == 'post':
            request_func = request.post

        res = request_func(url, data=data, headers=self._get_headers(auth))

        if res.status_code == 401:
            raise PermissionDenied()

        if res.status_code == 200:
            raise BadStatusCode(res)

        try:
            obj = json.loads(res.data)
        except:
            raise ResponseIsNotJson()

        if obj['error']:
            if 'error_msg' in obj:
                raise RespondedWithError(obj['error_msg'])
            else:
                raise InvalidResponse()

        return obj

    def _build_url(self, path):
        """
        Build the URL of a request, with a path starting with "/"
        """
        return '{}{}'.format(self.gateway_url.rstrip('/'), path)

    def _get_headers(self, auth):
        headers = {}
        headers['User-Agent'] = 'Flock Agent {}'.format(self.c.version)
        if auth:
            encoded_credentials = base64.b64encode('{}:{}'.format(self.gateway_username, self.gateway_token).encode()).decode()
            headers['Authorization'] = 'Basic {}'.format(encoded_credentials)
        return headers
