# -*- coding: utf-8 -*-
import os
import subprocess
from PyQt5 import QtCore, QtWidgets, QtGui

from .gui_common import Alert


class Bootstrap(object):
    """
    The object that makes sure Flock Agent has all its dependencies installed
    """
    def __init__(self, common):
        self.c = common
        self.c.log('Bootstrap', '__init__')

        self.homebrew_path = '/usr/local/bin/brew'

    def go(self):
        """
        Go through all the bootstrap steps
        """
        self.c.log('Bootstrap', 'go', 'Bootstrapping Flock Agent', always=True)

        self.c.log('Bootstrap', 'go', 'Making sure Homebrew is installed')
        if not os.path.exists(self.homebrew_path):
            message = '<b>Homebrew is not installed.</b><br>Follow the instructions at <a href="https://brew.sh">https://brew.sh</a><br>to install Homebrew and then run Flock again.'
            Alert(self.c, message, contains_links=True).launch()
            return False

        self.c.log('Bootstrap', 'go', 'Checking if osquery is installed')
        p = self.exec([self.homebrew_path, 'list'], capture_output=True)
        if not p:
            return False

        installed_packages = p.stdout.decode().split()
        osquery_installed = 'osquery' in installed_packages

        if not osquery_installed:
            self.c.log('Bootstrap', 'go', 'Checking if java is installed')
            p = self.exec([self.homebrew_path, 'cask', 'list'], capture_output=True)
            if not p:
                return False

            installed_casks = p.stdout.decode().split()
            java_installed = 'java' in installed_casks

            if not java_installed:
                # We can't automatically install the java cask because it needs root
                message = '<b>Java is not installed.</b><br>Click ok to install java using Homebrew. You will have to type your macOS password.<br>After it\'s installed, run Flock again.'
                if Alert(self.c, message, has_cancel_button=True).launch():
                    self.c.log('Bootstrap', 'go', 'Installing java in Terminal with: brew cask install java')
                    self.exec('osascript -e \'tell application "Terminal" to do script "brew cask install java && exit"\'')

                return False

            self.c.log('Bootstrap', 'go', 'Installing osquery')
            if not self.exec([self.homebrew_path, 'install', 'osquery']):
                return False

        self.c.log('Bootstrap', 'go', 'Configuring osquery')
        

        self.c.log('Bootstrap', 'go', 'Bootstrap complete')
        return True

    def exec(self, command, capture_output=False):
        try:
            if type(command) == list:
                self.c.log('Bootstrap', 'go', 'Executing: {}'.format(' '.join(command)), always=True)
                p = subprocess.run(command, capture_output=capture_output, check=True)
            else:
                self.c.log('Bootstrap', 'go', 'Executing: {}'.format(command), always=True)
                # If command is a string, shell must be true
                p = subprocess.run(command, shell=True, capture_output=capture_output, check=True)
            return p
        except subprocess.CalledProcessError:
            message = 'Error running <br><b>{}</b>.'.format(' '.join(command))
            Alert(self.c, message).launch()
            return False
