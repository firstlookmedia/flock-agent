# -*- coding: utf-8 -*-
import os
import subprocess
import shutil
from PyQt5 import QtCore, QtWidgets, QtGui

from .gui_common import Alert
from ..common import Platform


class Bootstrap(object):
    """
    The object that makes sure Flock Agent has all its dependencies installed
    """
    def __init__(self, common):
        self.c = common
        self.c.log('Bootstrap', '__init__')

    def go(self):
        """
        Go through all the bootstrap steps
        """
        platform = Platform.current()

        self.c.log('Bootstrap', 'go', 'Bootstrapping Flock Agent', always=True)

        self.c.log('Bootstrap', 'go', 'Making sure Flock Agent starts automatically')
        if platform == Platform.MACOS:
            autorun_filename = 'media.firstlook.flock_agent.plist'
            autorun_dir = os.path.expanduser("~/Library/LaunchAgents")
            os.makedirs(autorun_dir, exist_ok=True)
            shutil.copy(
                self.c.get_resource_path(os.path.join('autostart/macos', autorun_filename)),
                os.path.join(autorun_dir, autorun_filename)
            )
        elif platform == Platform.LINUX:
            pass
        else:
            self.c.log("Bootstrap", 'go', 'Unknown platform, unable to make Flock Agent start automatically')

        self.c.log('Bootstrap', 'go', 'Making sure osquery is installed')
        if not os.path.exists('/usr/local/bin/osqueryd') or not os.path.exists('/usr/local/bin/osqueryi'):
            message = '<b>Osquery is not installed (but it really should be).</b><br><br>You can either install it with Homebrew, or download it from <a href="https://osquery.io/downloads">https://osquery.io/downloads</a>. Install osquery and then run Flock again.'
            Alert(self.c, message, contains_links=True).launch()
            return False

        self.c.log('Bootstrap', 'go', 'Ensuring osquery data directory exists')
        try:
            os.makedirs(self.c.osquery.dir, exist_ok=True)
            os.makedirs(self.c.osquery.log_dir, exist_ok=True)
        except:
            message = '<b>Error creating directory:<br>{}</b><br><br>Maybe your permissions are wrong. Click ok to fix your permissions. You will have to type your macOS password.<br><br>After it\'s fixed, run Flock again.'.format(self.c.osquery.dir)
            if Alert(self.c, message, has_cancel_button=True).launch():
                self.c.log('Bootstrap', 'go', 'Fixing permissions: sudo chown -R "$USER":admin /usr/local/var')
                self.exec('osascript -e \'tell application "Terminal" to do script "sudo chown -R \\"$USER\\":admin /usr/local/var && exit"\'')

            return False

        self.c.log('Bootstrap', 'go', 'Refreshing osquery daemon')
        self.c.osquery.refresh_osqueryd()

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
