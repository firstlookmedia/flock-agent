# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from urllib.parse import urlparse

from .gui_common import Alert
from ..api_client import FlockApiClient, PermissionDenied, BadStatusCode, \
    ResponseIsNotJson, RespondedWithError, InvalidResponse, ConnectionError


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
        if self.c.settings.get('gateway_url') and self.c.settings.get('gateway_token'):
            self.status = self.STATUS_REGISTERED
        else:
            self.status = self.STATUS_NOT_REGISTERED

        # Server
        self.server_label = QtWidgets.QLabel()
        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setPlaceholderText("https://")
        self.server_url_label = QtWidgets.QLabel()
        self.server_url_label.setStyleSheet(self.c.gui.css['SettingsTab server_url_label'])
        self.server_button = QtWidgets.QPushButton()
        self.server_button.clicked.connect(self.server_button_clicked)

        server_url_layout = QtWidgets.QHBoxLayout()
        server_url_layout.addWidget(self.server_url_edit, stretch=1)
        server_url_layout.addWidget(self.server_url_label, stretch=1)
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
            self.server_url_edit.show()
            self.server_url_label.hide()
            self.server_button.setEnabled(True)
            self.server_button.setText('Connect')

        elif self.status == self.STATUS_REGISTERED:
            self.server_label.setText('You\'re sending data to this server:')
            self.server_url_edit.hide()
            self.server_url_label.setText(self.c.settings.get('gateway_url'))
            self.server_url_label.show()
            self.server_button.setEnabled(True)
            self.server_button.setText('Change Server')

    def server_button_clicked(self):
        self.c.log('SettingsTab', 'server_button_clicked')

        if self.status == self.STATUS_NOT_REGISTERED:
            self.server_button.setEnabled(False)
            self.server_button.setText('Registering...')

            # Validate server URL
            server_url = self.server_url_edit.text()
            o = urlparse(server_url)
            if (o.scheme != 'http' and o.scheme != 'https') or (o.path != '' and o.path != '/') or \
                o.params != '' or o.query != '' or o.fragment != '':

                Alert(self.c, 'Invalid server URL').launch()
                return False

            # Save the server URL in settings
            self.c.settings.set('gateway_url', server_url)

            # Try to register
            self.c.log('SettingsTab', 'server_button_clicked', 'registering with server')
            api_client = FlockApiClient(self.c)
            try:
                api_client.register()
                api_client.ping()
                self.status = self.STATUS_REGISTERED
            except PermissionDenied:
                Alert(self.c, 'Permission denied').launch()
            except BadStatusCode as e:
                Alert(self.c, 'Bad status code: {}'.format(e)).launch()
            except ResponseIsNotJson:
                Alert(self.c, 'Server response is not JSON').launch()
            except RespondedWithError as e:
                Alert(self.c, 'Server error: {}'.format(e)).launch()
            except InvalidResponse:
                Alert(self.c, 'Server returned an invalid response').launch()
            except ConnectionError:
                Alert(self.c, 'Error connecting to server').launch()

        elif self.status == self.STATUS_REGISTERED:
            self.c.settings.set('gateway_url', None)
            self.c.settings.set('gateway_token', None)
            self.c.settings.save()
            self.status = self.STATUS_NOT_REGISTERED

        self.update_ui()

    def quit_clicked(self):
        self.c.log('SettingsTab', 'quit_clicked')
        self.quit_signal.emit()
