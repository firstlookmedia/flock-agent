# -*- coding: utf-8 -*-
import os
import inspect

from .display import Display
from .status import Status
from .install import Install
from .purge import Purge

from .items import ItemList


class FlockAgent(object):
    def __init__(self, version):
        self.version = version

        # Information about software to be installed
        self.software = {
            'osquery': {
                'version': '3.3.2',
                'url': 'https://pkg.osquery.io/darwin/osquery-3.3.2.pkg',
                'sha256': '6ac1baa9bd13fcf3bd4c1b20a020479d51e26a8ec81783be7a8692d2c4a9926a'
            },
            'openjdk': {
                'version': '11.0.2',
                'url': 'https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_osx-x64_bin.tar.gz',
                'sha256': 'f365750d4be6111be8a62feda24e265d97536712bc51783162982b8ad96a70ee',
                'install_path': '/Library/Java/JavaVirtualMachines/jdk-11.0.2.jdk',
                'extract_path': '/Library/Java/JavaVirtualMachines'
            },
            'logstash': {
                'version': '6.6.0',
                'url': 'https://artifacts.elastic.co/downloads/logstash/logstash-6.6.0.tar.gz',
                'sha256': '5a9a8b9942631e9d4c3dfb8d47075276e8c2cff343841145550cc0c1cfe7bba7',
                'install_path': '/private/var/flock-agent/opt/logstash-6.6.0',
                'extract_path': '/private/var/flock-agent/opt'
            }
        }

        # Path to config files within the module
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config')

        # Internal objects
        self.display = Display(self.version)
        self.status = Status(self.display, self.software, self.config_path)
        self.install = Install(self.display, self.status, self.software, self.config_path)
        self.purge = Purge(self.display, self.status)
        self.item_list = ItemList(self)

        self.display.banner()

    def exec_status(self):
        """
        Check the status of all software managed by Flock Agent
        """
        all_good = True
        for item in self.item_list:
            if not item.exec_status():
                all_good = False

        if not all_good:
            self.display.install_message()

        # all_good = True
        #
        # status = self.status.is_osquery_installed()
        # if not status:
        #     all_good = False
        #
        # status = self.status.is_osquery_configured()
        # if not status:
        #     all_good = False
        #
        # status = self.status.is_openjdk_installed()
        # if not status:
        #     all_good = False
        #
        # status = self.status.is_logstash_installed()
        # if not status:
        #     all_good = False
        #
        # if not all_good:
        #     self.display.install_message()

    def exec_install(self):
        """
        Install and configure software managed by Flock Agent
        """
        for item in self.item_list:
            if not item.exec_install():
                return

        # # Configure osquery
        # status = self.status.is_osquery_configured()
        # if not status:
        #     if not self.install.copy_files_as_root('/private/var/osquery/', ['osquery.conf', 'osquery.flags']):
        #         return self.quit_early()
        #
        #     status = self.status.is_osquery_configured()
        #     if not status:
        #         self.display.error('osquery could not be configured properly')
        #         return self.quit_early()
        #
        #     self.display.newline()
        #
        # # Install OpenJDK
        # status = self.status.is_openjdk_installed()
        # if not status:
        #     filename = self.install.download_software(self.software['openjdk'])
        #     if not filename:
        #         return self.quit_early()
        #
        #     self.install.extract_tarball_as_root(self.software['openjdk'], filename)
        #
        #     status = self.status.is_openjdk_installed()
        #     if not status:
        #         self.display.error('OpenJDK did not install successfully')
        #         return self.quit_early()
        #
        #     self.display.newline()
        #
        # # Install logstash
        # status = self.status.is_logstash_installed()
        # if not status:
        #     filename = self.install.download_software(self.software['logstash'])
        #     if not filename:
        #         return self.quit_early()
        #
        #     self.install.extract_tarball_as_root(self.software['logstash'], filename)
        #
        #     status = self.status.is_logstash_installed()
        #     if not status:
        #         self.display.error('Logstash did not install successfully')
        #         return self.quit_early()
        #
        #     self.display.newline()

    def exec_purge(self):
        """
        Completely remove software managed by Flock Agent
        """
        # Make list of filenames and directories to delete, and commands to run
        filenames = []
        dirs = []
        commands = []

        for item in self.item_list:
            item_filenames, item_dirs, item_commands = item.exec_purge()
            filenames += item_filenames
            dirs += item_dirs
            commands += item_commands

        # Delete everything
        self.purge.delete_files(filenames)
        self.purge.delete_dirs(dirs)
        self.purge.run_commands(commands)

        # Run status
        self.exec_status()

        # if self.status.is_osquery_installed():
        #     dirs.append('/private/var/osquery/')
        #     filenames.append('/usr/local/bin/osquery*')
        #     commands.append('pkgutil --forget com.facebook.osquery')
        #
        # if self.status.is_osquery_configured():
        #     filenames.append('/private/var/osquery/osquery.conf')
        #     filenames.append('/private/var/osquery/osquery.flags')
        #
        # if self.status.is_openjdk_installed():
        #     dirs.append('/Library/Java/JavaVirtualMachines/jdk-11.0.2.jdk')
        #
        # if self.status.is_logstash_installed():
        #     dirs.append('/private/var/flock-agent/opt/logstash-6.6.0')
