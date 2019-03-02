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

        # Keep track of the twig views
        self.twig_views = []

        # Label
        label = QtWidgets.QLabel("There is new data we'd like to collect from your computer. We recommend that enable all of it.")
        label.setWordWrap(True)

        # List of twigs
        self.twigs_layout = QtWidgets.QVBoxLayout()
        self.twigs_layout.addStretch()

        twigs_widget = QtWidgets.QWidget()
        twigs_widget.setLayout(self.twigs_layout)

        twigs_list = QtWidgets.QScrollArea()
        twigs_list.setWidgetResizable(True)
        twigs_list.setWidget(twigs_widget)

        # Buttons
        enable_all_button = QtWidgets.QPushButton("Enable All")
        enable_all_button.setStyleSheet(self.c.gui.css['OptInTab enable_all_button'])
        enable_all_button.setFlat(True)
        enable_all_button.clicked.connect(self.clicked_enable_all_button)
        apply_button = QtWidgets.QPushButton("Apply Changes")
        apply_button.clicked.connect(self.clicked_apply_button)

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

    def update_ui(self):
        self.c.log('OptInTab', 'update_ui')

        # Remove all twigs
        for twig_view in self.twig_views:
            # Remove the twig view from the layout
            self.twigs_layout.removeWidget(twig_view)
            twig_view.close()

            # Remove it from the list of twig views
            self.twig_views.remove(twig_view)

        # Add undecided twigs
        undecided_twig_ids = self.c.settings.get_undecided_twig_ids()
        for twig_id in undecided_twig_ids:
            twig_view = TwigView(self.c, twig_id)
            self.twig_views.append(twig_view)
            self.twigs_layout.addWidget(twig_view)

    def clicked_enable_all_button(self):
        self.c.log('OptInTab', 'clicked_enable_all_button')

    def clicked_apply_button(self):
        self.c.log('OptInTab', 'clicked_apply_button')
