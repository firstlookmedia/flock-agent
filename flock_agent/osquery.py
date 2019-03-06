# -*- coding: utf-8 -*-
import os
import subprocess
import json

from .twigs import twigs


class Osquery(object):
    """
    This class takes care of all interaction with osquery, including running queries,
    dynamically generating the config file, and making sure the daemon is running
    """
    def __init__(self, common):
        self.c = common
        self.c.log('Osquery', '__init__')

        self.osquery_dir = os.path.join(self.c.appdata_path, 'osquery')
        self.osquery_log_dir = os.path.join(self.osquery_dir, 'logs')
        self.osquery_config_filename = os.path.join(self.osquery_dir, 'osquery.conf')

        self.config_skeleton = {
          "options": {
            "config_plugin": "filesystem",
            "logger_plugin": "filesystem",
            "logger_path": self.osquery_log_dir,
            "schedule_splay_percent": "10",
            "utc": "true"
          },
          "schedule": {},
          "decorators": {
            "load": [
              "SELECT uuid AS host_uuid FROM system_info;",
              "SELECT user AS username FROM logged_in_users ORDER BY time DESC LIMIT 1;"
            ]
          }
        }

    def save_conf(self):
        """
        Rebuild the osquery config file based on the latest settings
        """
        self.c.log('Osquery', 'save_conf')
        config = self.config_skeleton.copy()
        for twig_id in self.c.settings.get_enabled_twig_ids():
            config['schedule'][twig_id] = {
                'query': twigs[twig_id]['query'],
                'interval': twigs[twig_id]['interval']
            }

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
