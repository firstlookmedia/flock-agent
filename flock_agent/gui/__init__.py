# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets

from .gui_common import GuiCommon
from .daemon_client import DaemonClient
from .bootstrap import Bootstrap
from .onboarding import Onboarding
from .main_window import MainWindow


def main(common):
    # Create the Qt app
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Attach the GuiCommon and DaemonClient objects to Common
    common.gui = GuiCommon(common)
    common.daemon = DaemonClient(common)

    # Run the bootstrap sequence
    bootstrap = Bootstrap(common)
    if not bootstrap.go():
        return

    # Create the main window
    main_window = MainWindow(app, common)

    # Onboarding wizard
    if common.settings.first_run:

        def show_main_window():
            main_window.update_ui()
            main_window.show()

        onboarding = Onboarding(common)
        onboarding.finished.connect(show_main_window)
        onboarding.go()
    else:
        # Show or hide main window?
        if (
            common.settings.get("use_server")
            and len(common.settings.get_undecided_twig_ids()) == 0
        ):
            main_window.hide()
        else:
            main_window.show()

    # Clean up when app quits
    def shutdown():
        main_window.shutdown()

    app.aboutToQuit.connect(shutdown)

    sys.exit(app.exec_())
