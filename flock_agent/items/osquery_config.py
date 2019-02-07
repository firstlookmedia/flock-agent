# -*- coding: utf-8 -*-
import os
from ..item_base import ItemBase


class OsqueryConfigItem(ItemBase):
    def exec_status(self):
        status = True
        if not self.status.exists_and_has_same_content('/private/var/osquery/osquery.conf', 'osquery.conf'):
            status = False
        if not self.status.exists_and_has_same_content('/private/var/osquery/osquery.flags', 'osquery.flags'):
            status = False
        self.display.status_check('osquery is configured properly', status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            if not self.install.copy_files_as_root('/private/var/osquery/', ['osquery.conf', 'osquery.flags']):
                return self.quit_early()

            status = self.exec_status()
            if not status:
                self.display.error('osquery could not be configured properly')
                return self.quit_early()

            self.display.newline()

        return True

    def exec_purge(self):
        filenames = [
            '/private/var/osquery/osquery.conf',
            '/private/var/osquery/osquery.flags'
        ]
        dirs = []
        commands = []
        return (filenames, dirs, commands)
