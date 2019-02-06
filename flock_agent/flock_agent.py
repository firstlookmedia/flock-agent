# -*- coding: utf-8 -*-
import os
import inspect

from .display import Display
from .status import Status
from .install import Install


class FlockAgent(object):
    def __init__(self, version):
        self.version = version

        # Information about software to be installed
        self.software = {
            'osquery': {
                'version': '3.3.2',
                'url': 'https://pkg.osquery.io/darwin/osquery-3.3.2.pkg',
                'sha256': '6ac1baa9bd13fcf3bd4c1b20a020479d51e26a8ec81783be7a8692d2c4a9926a'
            }
        }

        # Path to config files within the module
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config')

        # Internal objects
        self.display = Display(self.version)
        self.status = Status(self.display, self.software, self.config_path)
        self.install = Install(self.display, self.status, self.software, self.config_path)

    def exec_status(self):
        """
        Check the status of all software managed by Flock Agent
        """
        all_good = True

        status = self.status.is_osquery_installed()
        if not status:
            all_good = False

        status = self.status.is_osquery_configured()
        if not status:
            all_good = False

        print('')
        if not all_good:
            self.display.install_message()
            print('')

    def exec_install(self):
        """
        Install and configure software managed by Flock Agent
        """
        # Install osquery
        status = self.status.is_osquery_installed()
        if not status:
            filename = self.install.download_software(self.software['osquery'])
            if not filename:
                return self.quit_early()

            self.install.install_pkg(filename)

            status = self.status.is_osquery_installed()
            if not status:
                self.display.error('osquery did not install successfully')
                return self.quit_early()

        # Configure osquery
        status = self.status.is_osquery_configured()
        if not status:
            if not self.install.copy_file_as_root('/private/var/osquery/osquery.conf', 'osquery.conf'):
                return self.quit_early()
            if not self.install.copy_file_as_root('/private/var/osquery/osquery.flags', 'osquery.flags'):
                return self.quit_early()

            status = self.status.is_osquery_configured()
            if not status:
                self.display.error('osquery could not be configured properly')
                return self.quit_early()

        self.display.newline()

    def quit_early(self):
        self.display.error('Encountered an error, quitting early')
        self.display.newline()
