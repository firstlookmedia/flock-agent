# -*- coding: utf-8 -*-
import os
import inspect

from .display import Display
from .purge import Purge
from .items import ItemList


class FlockAgent(object):
    def __init__(self, version):
        self.version = version

        # Path to config files within the module
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config')

        # Internal objects
        self.display = Display(self.version)
        self.item_list = ItemList(self.display, self.config_path)

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

    def exec_install(self):
        """
        Install and configure software managed by Flock Agent
        """
        for item in self.item_list:
            if not item.exec_install():
                return

    def exec_purge(self):
        """
        Completely remove software managed by Flock Agent
        """
        # Make list of filenames and directories to delete, and commands to run
        filenames = []
        dirs = []
        commands = []

        for item in self.item_list:
            if item.exec_status():
                item_filenames, item_dirs, item_commands = item.exec_purge()
                filenames += item_filenames
                dirs += item_dirs
                commands += item_commands

        # Delete everything
        purge = Purge(self.display)
        if len(commands) > 0:
            purge.run_commands(commands)
        if len(filenames) > 0:
            purge.delete_files(filenames)
        if len(dirs) > 0:
            purge.delete_dirs(dirs)
