# -*- coding: utf-8 -*-
import subprocess
from ..item_base import ItemBase


class OsqueryItem(ItemBase):
    def exec_status(self):
        ret = None
        try:
            p = subprocess.run(['/usr/sbin/pkgutil', '--pkg-info', 'com.facebook.osquery'],
                capture_output=True, check=True)
            version = p.stdout.decode().split('\n')[1].split(' ')[1]
            status = version == self.software['osquery']['version']
        except subprocess.CalledProcessError:
            # osquery isn't installed
            status = False

        self.display.status_check('osquery {} is installed'.format(self.software['osquery']['version']), status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            filename = self.install.download_software(self.software['osquery'])
            if not filename:
                return self.quit_early()

            self.install.install_pkg(filename)

            status = self.exec_status()
            if not status:
                self.display.error('osquery did not install successfully')
                return self.quit_early()

            self.display.newline()

        return True

    def exec_purge(self):
        filenames = ['/usr/local/bin/osquery*']
        dirs = ['/private/var/osquery/']
        commands = ['pkgutil --forget com.facebook.osquery']
        return (filenames, dirs, commands)
