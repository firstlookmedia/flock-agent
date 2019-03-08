# -*- coding: utf-8 -*-
import os
import subprocess
import json
import shutil

from .api_client import FlockApiClient
from .twigs import twigs


class Osquery(object):
    """
    This class takes care of all interaction with osquery, including running queries,
    dynamically generating the config file, and making sure the daemon is running
    """
    def __init__(self, common):
        self.c = common
        self.c.log('Osquery', '__init__')

        self.dir = '/usr/local/var/osquery'
        self.log_dir = '/usr/local/var/osquery/logs'
        self.config_filename = os.path.join(self.dir, 'osquery.conf')
        self.results_filename = os.path.join(self.log_dir, 'osqueryd.results.log')
        self.plist_filename = os.path.expanduser('~/Library/LaunchAgents/com.facebook.osqueryd.plist')

        # Make sure directories exist
        os.makedirs(self.dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        # Define the skeleton osquery config file, without any twigs
        self.config_skeleton = {
          "options": {
            "config_plugin": "filesystem",
            "logger_plugin": "filesystem",
            "logger_path": self.log_dir,
            "logger_min_status": 1, # don't log INFO
            "schedule_splay_percent": "10",
            "utc": "true",
            "host_identifier": "uuid"
          },
          "schedule": {},
          "decorators": {
            "load": [
              "SELECT uuid AS host_uuid FROM system_info;",
              "SELECT user AS username FROM logged_in_users ORDER BY time DESC LIMIT 1;"
            ]
          }
        }

    def refresh_osqueryd(self):
        """
        Rebuild the osquery config file based on the latest settings, and restart
        the osqueryd daemon
        """
        self.c.log('Osquery', 'refresh_osqueryd', 'enabling twigs: {}'.format(', '.join(self.c.settings.get_enabled_twig_ids())))

        # Rebuild osquery config
        config = self.config_skeleton.copy()
        for twig_id in self.c.settings.get_enabled_twig_ids():
            config['schedule'][twig_id] = {
                'query': twigs[twig_id]['query'],
                'interval': twigs[twig_id]['interval'],
                'description': twigs[twig_id]['description']
            }

        # Stop osqueryd
        subprocess.run(['/bin/launchctl', 'unload', self.plist_filename])

        # Write the config file
        with open(self.config_filename, 'w') as config_file:
            json.dump(config, config_file, indent=4)

        # Copy the launchd plist into the correct place
        shutil.copyfile(
            self.c.get_resource_path('com.facebook.osqueryd.plist'),
            self.plist_filename
        )

        # Start osqueryd
        subprocess.run(['/bin/launchctl', 'load', self.plist_filename])

    def exec(self, query):
        """
        Run an osquery query, return the response as an object
        """
        self.c.log('Osquery', 'exec', query)
        try:
            p = subprocess.run(['/usr/local/bin/osqueryi', '--json', query], capture_output=True, check=True)
            return json.loads(p.stdout)

        except:
            # Error running query
            return None

    def submit_logs(self):
        """
        If there are new osquery result logs, forward them to the Flock server and
        truncate the result file.
        """
        self.c.log('Osquery', 'submit_logs')

        # Start an API client
        api_client = FlockApiClient(self.c)
        try:
            api_client.ping()
        except:
            self.c.log('Osquery', 'submit_logs', 'API is not configured properly', always=True)
            return

        # Keep track of the biggest timestamp we see
        biggest_timestamp = self.c.settings.get('last_osquery_result_timestamp')

        # Load the log file
        try:
            with open(self.results_filename, 'r') as results_file:
                for line in results_file.readlines():
                    line = line.strip()

                    try:
                        obj = json.loads(line)

                        if 'name' in obj:
                            name = obj['name']
                        else:
                            name = 'unknown'

                        if 'unixTime' in obj:
                            # If we haven't submitted this yet
                            if obj['unixTime'] > self.c.settings.get('last_osquery_result_timestamp'):
                                # Submit it
                                api_client.submit(line)
                                self.c.log('Osquery', 'submit_logs', 'submitted "{}" result'.format(name))

                            else:
                                # Already submitted
                                self.c.log('Osquery', 'submit_logs', 'skipping "{}" result, already submitted'.format(name))

                            # Update the biggest timestamp, if needed
                            if obj['unixTime'] > biggest_timestamp:
                                biggest_timestamp = obj['unixTime']

                        else:
                            self.c.log('Osquery', 'submit_logs', 'warning: unixTime not in line: {}'.format(line))

                    except json.decoder.JSONDecodeError:
                        self.c.log('Osquery', 'submit_logs', 'warning: line is not valid JSON: {}'.format(line))

            # Update timestamp in settings
            if self.c.settings.get('last_osquery_result_timestamp') < biggest_timestamp:
                self.c.settings.set('last_osquery_result_timestamp', biggest_timestamp)
                self.c.settings.save()


        except FileNotFoundError:
            self.c.log('Osquery', 'submit_logs', 'warning: file not found: {}'.format(self.results_filename))