# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from .settings_dialog import SettingsDialog
from .systray import SysTray


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, common):
        super(MainWindow, self).__init__()
        self.app = app
        self.c = common

        self.c.log("MainWindow", "__init__")

        self.setWindowTitle('Flock')
        self.setWindowIcon(self.c.gui.icon)

        flags = QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | \
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint | \
            QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # Header
        header_label = QtWidgets.QLabel('<b><font color="#3461bc">Flock</font></b> monitors your computer for security issues while respecting your privacy')
        header_label.setMinimumWidth(410)
        header_label.setTextFormat(QtCore.Qt.RichText)
        header_label.setWordWrap(True)
        header_label.setStyleSheet(self.c.gui.css['MainWindow header_label'])
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.c.gui.logo)
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addStretch()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Settings button on the status bar
        self.settings_button = QtWidgets.QPushButton()
        self.settings_button.setDefault(False)
        self.settings_button.setFlat(True)
        self.settings_button.setFixedWidth(40)
        self.settings_button.setIcon(QtGui.QIcon(common.get_resource_path('images/settings.png')))
        self.settings_button.clicked.connect(self.open_settings)

        # Status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.addPermanentWidget(self.settings_button)
        self.setStatusBar(self.status_bar)

        # System tray
        self.systray = SysTray(self.c)
        self.systray.activated.connect(self.toggle_window)

        # Limit the width to 500px
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.show()

    def closeEvent(self, e):
        """
        Intercept close event, and instead minimize to systray
        """
        self.c.log("MainWindow", "closeEvent", "Hiding window")
        self.hide()
        e.ignore()

    def toggle_window(self):
        self.c.log("MainWindow", "toggle_window")
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def open_settings(self):
        self.c.log("MainWindow", "open_settings")
        d = SettingsDialog(self.c)
        d.quit_signal.connect(self.quit)
        d.exec_()

    def quit(self):
        self.c.log("MainWindow", "quit")
        self.app.quit()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
