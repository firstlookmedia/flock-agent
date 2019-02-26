# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from PyQt5 import QtCore, QtWidgets

from .gui_common import GuiCommon
from .main_window import MainWindow


def main(common):
    # Create the Qt app
    app = QtWidgets.QApplication(sys.argv)

    # Attach the GuiCommon object to Common
    common.gui = GuiCommon(common)

    # Warn if homebrew is not installed
    if not os.path.exists('/usr/local/bin/brew'):
        message = '<b>Homebrew is not installed.</b><br>Follow the instructions at <a href="https://brew.sh">https://brew.sh</a><br>to install Homebrew and then run Flock again.'
        common.gui.alert(message, contains_links=True)
        return

    # Now create the main window
    main_window = MainWindow(app, common)

    # Clean up when app quits
    def shutdown():
        main_window.shutdown()
    app.aboutToQuit.connect(shutdown)

    sys.exit(app.exec_())
