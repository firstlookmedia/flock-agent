# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..twigs import TwigView


class OptInTab(QtWidgets.QWidget):
    """
    Prompt the user to opt-in to undecided twigs
    """
    refresh = QtCore.pyqtSignal()
    
    def __init__(self, common):
        super(OptInTab, self).__init__()
        self.c = common

        self.c.log('OptInTab', '__init__')

        # Label
        label = QtWidgets.QLabel("There is new data we'd like to collect from your computer. We recommend that enable all of it.")
        label.setWordWrap(True)

        # List of twigs
        twigs_layout = QtWidgets.QVBoxLayout()
        for twig_id in self.c.settings.get_undecided_twig_ids():
            twig_view = TwigView(self.c, twig_id)
            twigs_layout.addWidget(twig_view)
        twigs_layout.addStretch()

        twigs_widget = QtWidgets.QWidget()
        twigs_widget.setLayout(twigs_layout)

        twigs_list = QtWidgets.QScrollArea()
        twigs_list.setWidgetResizable(True)
        twigs_list.setWidget(twigs_widget)

        # Buttons
        enable_all_button = QtWidgets.QPushButton("Enable All")
        enable_all_button.setStyleSheet(self.c.gui.css['OptInTab enable_all_button'])
        enable_all_button.setFlat(True)
        apply_button = QtWidgets.QPushButton("Apply Changes")

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(enable_all_button)
        buttons_layout.addWidget(apply_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(twigs_list, stretch=1)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
