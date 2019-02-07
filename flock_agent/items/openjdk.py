# -*- coding: utf-8 -*-
import os
from ..item_base import ItemBase


class OpenJdkItem(ItemBase):
    def get_software(self):
        return {
            'name': 'openjdk',
            'version': '8u202-b08',
            'url': 'https://github.com/AdoptOpenJDK/openjdk8-binaries/releases/download/jdk8u202-b08/OpenJDK8U-jdk_x64_mac_hotspot_8u202b08.tar.gz',
            'sha256': '059f7c18faa6722aa636bbd79bcdff3aee6a6da5b34940b072ea6e3af85bbe1d',
            'install_path': '/Library/Java/JavaVirtualMachines/jdk8u202-b08',
            'extract_path': '/Library/Java/JavaVirtualMachines'
        }

    def exec_status(self):
        status = os.path.exists(self.get_software()['install_path'])
        self.display.status_check('OpenJDK {} is installed'.format(self.get_software()['version']), status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            filename = self.download_software(self.get_software())
            if not filename:
                return self.quit_early()

            self.extract_tarball_as_root(self.get_software(), filename)

            status = self.exec_status()
            if not status:
                self.display.error('OpenJDK did not install successfully')
                return self.quit_early()

            self.display.newline()

        return True

    def exec_purge(self):
        filenames = []
        dirs = [self.get_software()['install_path']]
        commands = []
        return (filenames, dirs, commands)
