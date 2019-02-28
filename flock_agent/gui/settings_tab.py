# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class SettingsTab(QtWidgets.QWidget):
    """
    Settings
    """
    quit_signal = QtCore.pyqtSignal()

    STATUS_NOT_REGISTERED = 0
    STATUS_REGISTERED = 1

    def __init__(self, common):
        super(SettingsTab, self).__init__()
        self.c = common

        self.c.log('SettingsTab', '__init__')

        # Determine server status
        if self.c.settings.get('gateway_token'):
            self.status = self.STATUS_REGISTERED
        else:
            self.status = self.STATUS_NOT_REGISTERED

        # Server
        self.server_label = QtWidgets.QLabel()
        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setPlaceholderText("https://")
        self.server_button = QtWidgets.QPushButton()
        self.server_button.clicked.connect(self.server_button_clicked)

        server_url_layout = QtWidgets.QHBoxLayout()
        server_url_layout.addWidget(self.server_url_edit)
        server_url_layout.addWidget(self.server_button)

        server_layout = QtWidgets.QVBoxLayout()
        server_layout.addWidget(self.server_label)
        server_layout.addLayout(server_url_layout)

        # Buttons
        quit_button = QtWidgets.QPushButton('Quit Flock Agent')
        quit_button.clicked.connect(self.quit_clicked)
        quit_button.setStyleSheet(self.c.gui.css['SettingsTab quit_button'])
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

        self.update_ui()

    def update_ui(self):
        # Not registered yet
        if self.status == self.STATUS_NOT_REGISTERED:
            self.server_label.setText('What\'s the address of the server you will send data to?')
            self.server_url_edit.setText('')
            self.server_button.setText('Connect')

    def server_button_clicked(self):
        self.c.log('SettingsTab', 'server_button_clicked')

        if self.status == self.STATUS_NOT_REGISTERED:
            # Try to register
            pass

    def quit_clicked(self):
        self.c.log('SettingsTab', 'quit_clicked')
        self.quit_signal.emit()
        self.accept()
