# -*- coding: utf-8 -*-
import requests


class FlockApiClient(object):
    """
    This is a client that interacts with the Flock gateway
    """
    def __init__(self, common):
        self.c = common
        self.c.log("FlockApiClient", "__init__")

    def init_config(self):
        """
        See if the API config that's stored in settings works or not. Returns True or False.
        """
        self.gateway_url = self.c.settings.get('gateway_url')
        self.gateway_token = self.c.settings.get('gateway_url')
        self.gateway_username = self.c.settings.get('gateway_url')

        if self.gateway_url and self.gateway_token and self.gateway_username:
            pass
