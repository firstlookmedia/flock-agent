# -*- coding: utf-8 -*-
import os
import subprocess
import json
import shutil

from .twigs import twigs


class Osquery(object):
    """
    This class takes care of all interaction with osquery, including running queries,
    dynamically generating the config file, and making sure the daemon is running
    """
    def __init__(self, common):
        self.c = common
        self.c.log('Osquery', '__init__')

        self.osquery_dir = '/usr/local/var/osquery'
        self.osquery_log_dir = '/usr/local/var/osquery/logs'
        self.osquery_config_filename = os.path.join(self.osquery_dir, 'osquery.conf')
        self.osquery_plist_filename = os.path.expanduser('~/Library/LaunchAgents/com.facebook.osqueryd.plist')

        self.config_skeleton = {
          "options": {
            "config_plugin": "filesystem",
            "logger_plugin": "filesystem",
            "logger_path": self.osquery_log_dir,
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

        # Make sure directories exist
        os.makedirs(self.osquery_dir, exist_ok=True)
        os.makedirs(self.osquery_log_dir, exist_ok=True)

        # Rebuild osquery config
        config = self.config_skeleton.copy()
        for twig_id in self.c.settings.get_enabled_twig_ids():
            config['schedule'][twig_id] = {
                'query': twigs[twig_id]['query'],
                'interval': twigs[twig_id]['interval']
            }

        # Stop osqueryd
        subprocess.run(['/bin/launchctl', 'unload', self.osquery_plist_filename])

        # Write the config file
        with open(self.osquery_config_filename, 'w') as config_file:
            json.dump(config, config_file, indent=4)

        # Copy the launchd plist into the correct place
        shutil.copyfile(
            self.c.get_resource_path('com.facebook.osqueryd.plist'),
            self.osquery_plist_filename
        )

        # Start osqueryd
        subprocess.run(['/bin/launchctl', 'load', self.osquery_plist_filename])

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
