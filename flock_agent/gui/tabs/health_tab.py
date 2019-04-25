# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from urllib.parse import urlparse


class HealthTab(QtWidgets.QWidget):
    """
    Health
    """
    def __init__(self, common):
        super(HealthTab, self).__init__()
        self.c = common

        self.c.log('HealthTab', '__init__')

        self.update_ui()

    def update_ui(self):
        pass
