# -*- coding: utf-8 -*-
import subprocess
from ..item_base import ItemBase


class OsqueryItem(ItemBase):
    def get_software(self):
        return {
            'name': 'osquery',
            'version': '3.3.2',
            'url': 'https://pkg.osquery.io/darwin/osquery-3.3.2.pkg',
            'sha256': '6ac1baa9bd13fcf3bd4c1b20a020479d51e26a8ec81783be7a8692d2c4a9926a'
        }

    def exec_status(self):
        ret = None
        try:
            p = subprocess.run(['/usr/sbin/pkgutil', '--pkg-info', 'com.facebook.osquery'],
                capture_output=True, check=True)
            version = p.stdout.decode().split('\n')[1].split(' ')[1]
            status = version == self.get_software()['version']
        except subprocess.CalledProcessError:
            # osquery isn't installed
            status = False

        self.display.status_check('osquery {} is installed'.format(self.get_software()['version']), status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            filename = self.download_software(self.get_software())
            if not filename:
                return self.quit_early()

            self.install_pkg(filename)

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
