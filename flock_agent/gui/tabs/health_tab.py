# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..health import *
from ...common import Platform


class HealthTab(QtWidgets.QWidget):
    """
    Health
    """
    def __init__(self, common):
        super(HealthTab, self).__init__()
        self.c = common

        self.c.log('HealthTab', '__init__')

        # Health items
        if Platform.current() == Platform.MACOS:
            self.health_items = [
                HealthItemMacOSFileVault(self.c),
                HealthItemMacOSGatekeeper(self.c),
                HealthItemMacOSFirewall(self.c),
                HealthItemMacOSRemoteSharing(self.c),
                HealthItemMacOSAutoUpdates(self.c),
                HealthItemMacOSGuestUser(self.c),
                HealthItemMacOSSIP(self.c)
            ]
        else:
            self.health_items = []
        health_item_layout = QtWidgets.QVBoxLayout()
        for health_item in self.health_items:
            health_item_layout.addWidget(health_item)

        # Buttons
        refresh_button = QtWidgets.QPushButton("Refresh Health Check")
        refresh_button.clicked.connect(self.clicked_refresh_button)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(refresh_button)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(health_item_layout)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def clicked_refresh_button(self):
        self.c.log('HealthTab', 'clicked_refresh_button')
        for health_item in self.health_items:
            health_item.refresh()
