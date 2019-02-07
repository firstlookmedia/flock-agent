# -*- coding: utf-8 -*-

class ItemBase(object):
    """
    An item is a piece of software or configuration that can be installed or purged
    """
    def __init__(self, agent):
        self.display = agent.display
        self.status = agent.status
        self.install = agent.install
        self.purge = agent.purge
        self.software = agent.software
        self.config_path = agent.config_path

    def exec_status(self):
        """
        To be overridden by child classes
        Checks to see if this item is installed
        """
        pass

    def exec_install(self):
        """
        To be overridden by child classes
        Installs this item, if it's not already installed
        """
        pass

    def exec_purge(self):
        """
        To be overridden by child classes
        Returns a tuple (filenames, dirs, commands) with a list of filenames and dirs
        to delete, and commands to run, all as root, to uninstall this item
        """
        pass

    def quit_early(self):
        self.display.error('Encountered an error, quitting early')
        self.display.newline()
        return False
