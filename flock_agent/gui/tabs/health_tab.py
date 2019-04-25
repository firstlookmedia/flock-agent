# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..health import HealthItemFileVault, HealthItemGatekeeper, \
                     HealthItemFirewall, HealthItemRemoteSharing, \
                     HealthItemAutoUpdates, HealthItemGuestUser, \
                     HealthItemSIP


class HealthTab(QtWidgets.QWidget):
    """
    Health
    """
    def __init__(self, common):
        super(HealthTab, self).__init__()
        self.c = common

        self.c.log('HealthTab', '__init__')

        # Load images
        good_pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/health_good.png")))
        bad_pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/health_bad.png")))

        # Health items
        self.health_items = [
            HealthItemFileVault(self.c, good_pixmap, bad_pixmap),
            HealthItemGatekeeper(self.c, good_pixmap, bad_pixmap),
            HealthItemFirewall(self.c, good_pixmap, bad_pixmap),
            HealthItemRemoteSharing(self.c, good_pixmap, bad_pixmap),
            HealthItemAutoUpdates(self.c, good_pixmap, bad_pixmap),
            HealthItemGuestUser(self.c, good_pixmap, bad_pixmap),
            HealthItemSIP(self.c, good_pixmap, bad_pixmap)
        ]

        # Layout
        layout = QtWidgets.QVBoxLayout()
        for health_item in self.health_items:
            layout.addWidget(health_item)
        layout.addStretch()
        self.setLayout(layout)

        self.update_ui()

    def update_ui(self):
        pass
