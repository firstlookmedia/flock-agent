# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class SettingsDialog(QtWidgets.QDialog):
    """
    Flock Agent settings
    """
    quit_signal = QtCore.pyqtSignal()

    def __init__(self, common):
        super(SettingsDialog, self).__init__()
        self.c = common

        self.c.log('SettingsDialog', '__init__')

        flags = QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | \
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint | \
            QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setWindowTitle('Flock Settings')
        self.setWindowIcon(self.c.gui.icon)
        self.setModal(True)
        self.setSizeGripEnabled(False)

        # Server
        self.server_label = QtWidgets.QLabel('What\'s the address of the server you will send data to?')
        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setPlaceholderText("https://")
        self.server_button = QtWidgets.QPushButton('Connect')

        server_url_layout = QtWidgets.QHBoxLayout()
        server_url_layout.addWidget(self.server_url_edit)
        server_url_layout.addWidget(self.server_button)

        server_layout = QtWidgets.QVBoxLayout()
        server_layout.addWidget(self.server_label)
        server_layout.addLayout(server_url_layout)

        # Buttons
        quit_button = QtWidgets.QPushButton('Quit Flock Agent')
        quit_button.clicked.connect(self.quit_clicked)
        quit_button.setStyleSheet(self.c.gui.css['SettingsDialog quit_button'])
        quit_button.setFlat(True)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(quit_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(server_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def quit_clicked(self):
        self.c.log('SettingsDialog', 'quit_clicked')
        self.quit_signal.emit()
        self.accept()
