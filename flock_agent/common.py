# -*- coding: utf-8 -*-
import os
import sys
import inspect
import json

from .settings import Settings
from .osquery import Osquery
from .api_client import FlockApiClient


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
        self.osquery.refresh_osqueryd()

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

    def check_osquery_logs(self):
        """
        If there are new osquery result logs, forward them to the Flock server and
        truncate the result file.
        """
        self.log('Common', 'check_osquery_logs')

        # Start an API client
        api_client = FlockApiClient(self.c)
        try:
            api_client.ping()
        except:
            self.log('Common', 'check_osquery_logs', 'API is not configured properly')
            return

        # Keep track of the biggest timestamp we see
        biggest_timestamp = self.settings.get('last_osquery_result_timestamp')

        # Load the log file
        try:
            with open(self.osquery.results_filename, 'r') as results_file:
                for line in results_file.readlines():
                    try:
                        obj = json.loads(line)
                        if 'unixTime' in obj:
                            # If we haven't imported this yet
                            if obj['unixTime'] > self.settings.get('last_osquery_result_timestamp'):
                                pass

                            # Update the biggest timestamp, if needed
                            if obj['unixTime'] > biggest_timestamp:
                                biggest_timestamp = obj['unixTime']

                        else:
                            self.log('Common', 'check_osquery_logs', 'warning: unixTime not in line: {}'.format(line.strip()))

                    except json.decoder.JSONDecodeError:
                        self.log('Common', 'check_osquery_logs', 'warning: line is not valid JSON: {}'.format(line.strip()))


        except FileNotFoundError:
            self.log('Common', 'check_osquery_logs', 'warning: file not found: {}'.format(self.osquery.results_filename))
