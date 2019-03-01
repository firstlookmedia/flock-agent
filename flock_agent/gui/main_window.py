# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from .twigs_tab import TwigsTab
from .settings_tab import SettingsTab
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
        #self.setWindowFlags(flags)

        # Header
        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/icon.png"))))
        header_label = QtWidgets.QLabel('<b><font color="#3461bc">Flock</font></b> monitors your computer for security issues while respecting your privacy')
        header_label.setTextFormat(QtCore.Qt.RichText)
        header_label.setWordWrap(True)
        header_label.setStyleSheet(self.c.gui.css['MainWindow header_label'])
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addWidget(header_label, stretch=1)
        header_layout.addStretch()

        # Tabs
        self.twigs_tab = TwigsTab(self.c)

        self.settings_tab = SettingsTab(self.c)
        self.settings_tab.quit_signal.connect(self.quit)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.twigs_tab, "Data")
        tabs.addTab(self.settings_tab, "Settings")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(tabs, stretch=1)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # System tray
        self.systray = SysTray(self.c)
        self.systray.activated.connect(self.toggle_window)

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

    def quit(self):
        self.c.log("MainWindow", "quit")
        self.app.quit()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
