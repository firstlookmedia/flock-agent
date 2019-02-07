# -*- coding: utf-8 -*-
import os
import subprocess
from ..item_base import ItemBase


class OpenJdkItem(ItemBase):
    def get_software(self):
        return {
            'name': 'openjdk',
            'version': '11.0.2',
            'url': 'https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_osx-x64_bin.tar.gz',
            'sha256': 'f365750d4be6111be8a62feda24e265d97536712bc51783162982b8ad96a70ee',
            'install_path': '/Library/Java/JavaVirtualMachines/jdk-11.0.2.jdk',
            'extract_path': '/Library/Java/JavaVirtualMachines'
        }

    def exec_status(self):
        status = os.path.exists(self.get_software()['install_path'])
        self.display.status_check('OpenJDK {} is installed'.format(self.get_software()['version']), status)
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
                self.display.error('OpenJDK did not install successfully')
                return self.quit_early()

            self.display.newline()

        return True

    def exec_purge(self):
        filenames = []
        dirs = ['/Library/Java/JavaVirtualMachines/jdk-11.0.2.jdk']
        commands = []
        return (filenames, dirs, commands)
