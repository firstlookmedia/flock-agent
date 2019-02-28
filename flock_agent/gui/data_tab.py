# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class DataTab(QtWidgets.QWidget):
    """
    Toggle data types that Flock Agent sends to the server
    """
    quit_signal = QtCore.pyqtSignal()

    def __init__(self, common):
        super(DataTab, self).__init__()
        self.c = common

        self.c.log('DataTab', '__init__')

        # Label
        label = QtWidgets.QLabel('This is the data tab')

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
