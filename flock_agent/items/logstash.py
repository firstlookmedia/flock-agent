# -*- coding: utf-8 -*-
import os
from ..item_base import ItemBase


class LogstashItem(ItemBase):
    def get_software(self):
        return {
            'name': 'logstash',
            'version': '6.6.0',
            'url': 'https://artifacts.elastic.co/downloads/logstash/logstash-6.6.0.tar.gz',
            'sha256': '5a9a8b9942631e9d4c3dfb8d47075276e8c2cff343841145550cc0c1cfe7bba7',
            'install_path': '/private/var/flock-agent/opt/logstash-6.6.0',
            'extract_path': '/private/var/flock-agent/opt'
        }

    def exec_status(self):
        status = os.path.exists(self.get_software()['install_path'])
        self.display.status_check('Logstash {} is installed'.format(self.get_software()['version']), status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            filename = self.install.download_software(self.get_software())
            if not filename:
                return self.quit_early()

            self.install.extract_tarball_as_root(self.get_software(), filename)

            status = self.exec_status()
            if not status:
                self.display.error('Logstash did not install successfully')
                return self.quit_early()

            self.display.newline()

        return True

    def exec_purge(self):
        filenames = []
        dirs = ['/private/var/flock-agent/opt/logstash-6.6.0']
        commands = []
        return (filenames, dirs, commands)
