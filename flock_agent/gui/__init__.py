# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets

from .gui_common import GuiCommon
from .daemon_client import DaemonClient
from .bootstrap import Bootstrap
from .onboarding import Onboarding
from .main_window import MainWindow


# Different versions of PyQt5 have differences in QtCore.Qt.CheckState
# Monkey patch them here
try:
    checked = QtCore.Qt.CheckState.Checked
except:
    QtCore.Qt.CheckState.Checked = QtCore.Qt.Checked
    QtCore.Qt.CheckState.Unchecked = QtCore.Qt.Unchecked


def main(common):
    # Create the Qt app
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Attach the GuiCommon and DaemonClient objects to Common
    common.gui = GuiCommon(common, app)
    common.daemon = DaemonClient(common)

    # Run the bootstrap sequence
    bootstrap = Bootstrap(common)
    if not bootstrap.go():
        return

    # Create the main window
    main_window = MainWindow(app, common)

    # Onboarding wizard
    if common.gui.settings.get("first_run"):

        def show_main_window():
            main_window.update_ui()
            main_window.show()

        onboarding = Onboarding(common)
        onboarding.finished.connect(show_main_window)
        onboarding.go()
    else:
        # Show or hide main window?
        if (
            common.daemon.get("use_server")
            and len(common.daemon.get_undecided_twig_ids()) == 0
        ):
            main_window.hide()
        else:
            main_window.show()

    # Clean up when app quits
    def shutdown():
        main_window.shutdown()

    app.aboutToQuit.connect(shutdown)

    sys.exit(app.exec_())
