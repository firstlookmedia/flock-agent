# -*- coding: utf-8 -*-
import os
from ..item_base import ItemBase


class OsqueryConfigItem(ItemBase):
    def exec_status(self):
        status = True
        if not self.is_conf_file_installed('/private/var/osquery/osquery.conf', 'osquery.conf'):
            status = False
        if not self.is_conf_file_installed('/private/var/osquery/osquery.flags', 'osquery.flags'):
            status = False
        if not os.path.exists('/Library/LaunchDaemons/com.facebook.osqueryd.plist'):
            status = False

        # Note, this isn't checking to see if the launchd is currently running because to do that
        # we need root, and I don't want to prompt for a password on status. To do that:
        # $ sudo launchctl list |grep com.facebook.osqueryd

        self.display.status_check('osquery is configured properly', status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            if not self.copy_conf_files('/private/var/osquery/', ['osquery.conf', 'osquery.flags']):
                return self.quit_early()

            if not self.install_launchd('/private/var/osquery/com.facebook.osqueryd.plist'):
                return self.quit_early()

            status = self.exec_status()
            if not status:
                self.display.error('osquery could not be configured properly')
                return self.quit_early()

            self.display.newline()

        return True

    def exec_purge(self):
        filenames = [
            '/Library/LaunchDaemons/com.facebook.osqueryd.plist',
            '/private/var/osquery/osquery.conf',
            '/private/var/osquery/osquery.flags'
        ]
        dirs = []
        commands = [
            '/bin/launchctl unload /Library/LaunchDaemons/com.facebook.osqueryd.plist'
        ]
        return (filenames, dirs, commands)
