# -*- coding: utf-8 -*-
import os
import sys
import inspect
import json
import platform
import appdirs


class Common(object):
    """
    The Common class is a singleton of shared functionality throughout the app
    """
    def __init__(self, verbose, version):
        self.verbose = verbose
        self.log('Common', '__init__')

        self.version = version
        self.appdata_path = appdirs.user_config_dir("FlockAgent")

    def log(self, module, func, msg='', always=False):
        if self.verbose:
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
            if Platform.current() == Platform.MACOS:
                prefix = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'Resources/share')
            elif Platform.current() == Platform.LINUX:
                prefix = os.path.join(sys.prefix, 'share/flock-agent')

        resource_path = os.path.join(prefix, filename)
        return resource_path


class Platform:
    MACOS = 'macos'
    LINUX = 'linux'
    UNKNOWN = 'unknown'

    @staticmethod
    def current():
        system = platform.system()
        if system == 'Darwin':
            return Platform.MACOS
        elif system == 'Linux':
            return Platform.LINUX
        else:
            return Platform.UNKNOWN