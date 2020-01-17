# -*- coding: utf-8 -*-
import logging
import os
import shutil
import subprocess
import time

import appdirs

from .gui_common import Alert
from .daemon_client import DaemonNotRunningException, PermissionDeniedException
from ..common import Platform


class Bootstrap(object):
    """
    The object that makes sure Flock Agent has all its dependencies installed
    """

    def __init__(self, common):
        self.c = common
        logger = logging.getLogger("Bootstrap.__init__")
        logger.debug("")

    def go(self):
        """
        Go through all the bootstrap steps
        """
        platform = Platform.current()

        logger = logging.getLogger("Bootstrap.go")
        logger.warning("Bootstrapping Flock Agent")

        if platform == Platform.UNKNOWN:
            logger.warning(
                "Unknown platform: Unable to make sure Flock Agent starts automatically",
            )
        else:
            logger.info("Making sure Flock Agent starts automatically")
            if platform == Platform.MACOS:
                autorun_dir = os.path.expanduser("~/Library/LaunchAgents")
                autorun_filename = "media.firstlook.flock-agent.plist"
                src_filename = self.c.get_resource_path(
                    os.path.join("autostart/macos", autorun_filename)
                )
            elif platform == Platform.LINUX:
                autorun_dir = appdirs.user_config_dir("autostart")
                autorun_filename = "media.firstlook.flock-agent.desktop"
                src_filename = self.c.get_resource_path(
                    os.path.join("autostart/linux", autorun_filename)
                )

            os.makedirs(autorun_dir, exist_ok=True)
            shutil.copy(src_filename, os.path.join(autorun_dir, autorun_filename))

        if platform == Platform.UNKNOWN:
            logger.warning("Unknown platform: Unable to make sure osquery is installed")
        else:
            logger.warning("Making sure osquery is installed")
            if platform == Platform.MACOS:
                # macOS version doesn't check for osqueryi, which is just a symlink of
                # osqueryd anyway -- the daemon's Osquery object the symlink if it isn't there
                if not os.path.exists("/usr/local/bin/osqueryd"):
                    message = (
                        "<b>Osquery is not installed.</b><br><br>You can either install it with Homebrew, or download it from "
                        '<a href="https://osquery.io/downloads">https://osquery.io/downloads</a>. Install osquery and then run Flock again.'
                    )
                    Alert(self.c, message, contains_links=True).launch()
                    return False
            elif platform == Platform.LINUX:
                if not os.path.exists("/usr/bin/osqueryd") or not os.path.exists(
                    "/usr/bin/osqueryi"
                ):
                    message = (
                        "<b>Osquery is not installed.</b><br><br>To add the osquery repository to your system and install the osquery package, follow "
                        'the instructions at <a href="https://osquery.io/downloads">https://osquery.io/downloads</a> under "Alternative Install '
                        'Options".<br><br>For Debian, Ubuntu, or Mint, follow the "Debian Linux" instructions, and for Fedora, Red Hat, or CentOS, follow the '
                        '"RPM Linux" instructions.<br><br>Install osquery and then run Flock again.'
                    )
                    Alert(self.c, message, contains_links=True).launch()
                    return False

        logger.info("Making sure the Flock Agent daemon is running")
        connected = False
        permission_denied = False
        for _ in range(5):
            try:
                self.c.daemon.ping()
                connected = True
                break
            except DaemonNotRunningException:
                logger.info("Failed to connect to daemon ...")
                time.sleep(1)
            except PermissionDeniedException:
                logger.info("Permission denied ...")
                permission_denied = True
                time.sleep(1)
        if not connected:
            if permission_denied:
                self.c.gui.daemon_permission_denied()
            else:
                self.c.gui.daemon_not_running()
            return False

        logger.info("Bootstrap complete")
        return True

    def exec(self, command, capture_output=False):
        try:
            if type(command) == list:
                logger = logging.getLogger("Bootstrap.exec")
                logger.warning("Executing: {' '.join(command)}")
                p = subprocess.run(command, capture_output=capture_output, check=True)
            else:
                logger.warning("Executing: {command}")
                # If command is a string, shell must be true
                p = subprocess.run(
                    command, shell=True, capture_output=capture_output, check=True
                )
            return p
        except subprocess.CalledProcessError:
            message = "Error running <br><b>{}</b>.".format(" ".join(command))
            Alert(self.c, message).launch()
            return False
