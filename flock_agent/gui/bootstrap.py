# -*- coding: utf-8 -*-
import os
import subprocess
import shutil
import appdirs
from PyQt5 import QtCore, QtWidgets, QtGui

from .gui_common import Alert
from .daemon_client import DaemonNotRunningException, PermissionDeniedException
from ..common import Platform


class Bootstrap(object):
    """
    The object that makes sure Flock Agent has all its dependencies installed
    """

    def __init__(self, common):
        self.c = common
        self.c.log("Bootstrap", "__init__")

    def go(self):
        """
        Go through all the bootstrap steps
        """
        platform = Platform.current()

        self.c.log("Bootstrap", "go", "Bootstrapping Flock Agent", always=True)

        if platform == Platform.UNKNOWN:
            self.c.log(
                "Bootstrap",
                "go",
                "Unknown platform: Unable to make sure Flock Agent starts automatically",
            )
        else:
            self.c.log(
                "Bootstrap", "go", "Making sure Flock Agent starts automatically"
            )
            if platform == Platform.MACOS:
                autorun_dir = os.path.expanduser("~/Library/LaunchAgents")
                autorun_filename = "media.firstlook.flock-agent.plist"
                src_filename = self.c.get_resource_path(
                    os.path.join("autostart/macos", autorun_filename)
                )
            elif platform == Platform.LINUX:
                autorun_dir = appdirs.user_config_dir("autostart")
                autorun_filename = "autostart/linux/media.firstlook.flock-agent.desktop"
                src_filename = self.c.get_resource_path(
                    os.path.join("autostart/linux", autorun_filename)
                )

            os.makedirs(autorun_dir, exist_ok=True)
            shutil.copy(src_filename, os.path.join(autorun_dir, autorun_filename))

        if platform == Platform.UNKNOWN:
            self.c.log(
                "Bootstrap",
                "go",
                "Unknown platform: Unable to make sure osquery is installed",
            )
        else:
            self.c.log("Bootstrap", "go", "Making sure osquery is installed")
            if platform == Platform.MACOS:
                if not os.path.exists("/usr/local/bin/osqueryd") or not os.path.exists(
                    "/usr/local/bin/osqueryi"
                ):
                    message = '<b>Osquery is not installed.</b><br><br>You can either install it with Homebrew, or download it from <a href="https://osquery.io/downloads">https://osquery.io/downloads</a>. Install osquery and then run Flock again.'
                    Alert(self.c, message, contains_links=True).launch()
                    return False
            elif platform == Platform.LINUX:
                if not os.path.exists("/usr/bin/osqueryd") or not os.path.exists(
                    "/usr/bin/osqueryi"
                ):
                    message = '<b>Osquery is not installed.</b><br><br>To add the osquery repository to your system and install the osquery package, follow the instructions at <a href="https://osquery.io/downloads">https://osquery.io/downloads</a> under "Alternative Install Options".<br><br>For Debian, Ubuntu, or Mint, follow the "Debian Linux" instructions, and for Fedora, Red Hat, or CentOS, follow the "RPM Linux" instructions.<br><br>Install osquery and then run Flock again.'
                    Alert(self.c, message, contains_links=True).launch()
                    return False

        self.c.log("Bootstrap", "go", "Making sure the Flock Agent daemon is running")
        try:
            self.c.daemon.ping()
        except DaemonNotRunningException:
            self.c.gui.daemon_not_running()
            return False
        except PermissionDeniedException:
            self.c.gui.daemon_permission_denied()
            return False

        self.c.log("Bootstrap", "go", "Bootstrap complete")
        return True

    def exec(self, command, capture_output=False):
        try:
            if type(command) == list:
                self.c.log(
                    "Bootstrap",
                    "go",
                    "Executing: {}".format(" ".join(command)),
                    always=True,
                )
                p = subprocess.run(command, capture_output=capture_output, check=True)
            else:
                self.c.log(
                    "Bootstrap", "go", "Executing: {}".format(command), always=True
                )
                # If command is a string, shell must be true
                p = subprocess.run(
                    command, shell=True, capture_output=capture_output, check=True
                )
            return p
        except subprocess.CalledProcessError:
            message = "Error running <br><b>{}</b>.".format(" ".join(command))
            Alert(self.c, message).launch()
            return False
