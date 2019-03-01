# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..twigs import TwigView


class TwigsTab(QtWidgets.QWidget):
    """
    List of twigs that have been decided on
    """
    def __init__(self, common):
        super(TwigsTab, self).__init__()
        self.c = common

        self.c.log('TwigsTab', '__init__')

        # Label
        label = QtWidgets.QLabel("This is the data that we're collecting from your computer:")
        label.setWordWrap(True)

        # List of twigs
        twigs_layout = QtWidgets.QVBoxLayout()
        for twig_id in self.c.settings.get_decided_twig_ids():
            twig_view = TwigView(self.c, twig_id)
            twigs_layout.addWidget(twig_view)
        twigs_layout.addStretch()

        twigs_widget = QtWidgets.QWidget()
        twigs_widget.setLayout(twigs_layout)

        twigs_list = QtWidgets.QScrollArea()
        twigs_list.setWidgetResizable(True)
        twigs_list.setWidget(twigs_widget)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(twigs_list, stretch=1)
        self.setLayout(layout)
