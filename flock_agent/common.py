# -*- coding: utf-8 -*-
import os
import sys
import inspect
import json

from .settings import Settings
from .osquery import Osquery


class Common(object):
    """
    The Common class is a singleton of shared functionality throughout the app
    """
    def __init__(self, debug, version):
        self.debug = debug
        self.log('Common', '__init__')

        self.version = version
        self.appdata_path = os.path.expanduser("~/Library/Application Support/Flock Agent")

        # Load settings
        self.settings = Settings(self)

        # Create an osquery object
        self.osquery = Osquery(self)

    def log(self, module, func, msg='', always=False):
        if self.debug:
            final_msg = "○ {}.{}".format(module, func)
            if msg:
                final_msg = "{}: {}".format(final_msg, msg)
            print(final_msg)

        elif always:
            print("○ {}".format(msg))

    def get_resource_path(self, filename):
        # In dev mode, look for resources directory relative to python file
        if getattr(sys, 'flock_agent_dev', False):
            prefix = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))), 'share')

        # Otherwise assume the app is "frozen" in an app bundle
        else:
            prefix = os.path.join(os.path.dirname(sys.executable), 'share')

        resource_path = os.path.join(prefix, filename)

        #self.log('Common', 'get_resource_path', resource_path)
        return resource_path
