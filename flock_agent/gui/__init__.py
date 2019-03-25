# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets

from .gui_common import GuiCommon
from .bootstrap import Bootstrap
from .main_window import MainWindow


def main(common):
    # Create the Qt app
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Attach the GuiCommon object to Common
    common.gui = GuiCommon(common)

    # Run the bootstrap sequence
    bootstrap = Bootstrap(common)
    if not bootstrap.go():
        return

    # Now create the main window
    main_window = MainWindow(app, common)

    # Clean up when app quits
    def shutdown():
        main_window.shutdown()
    app.aboutToQuit.connect(shutdown)

    sys.exit(app.exec_())
