# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

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
        header_label.setStyleSheet(self.c.gui.css['header-label'])
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

        # System tray
        self.systray = SysTray(self.c)
        self.systray.activated.connect(self.toggle_window)

        # Limit the width to 500px
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.show()

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def closeEvent(self, e):
        """
        Intercept close event, and instead minimize to systray
        """
        self.hide()
        e.ignore()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
