# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..twigs import TwigView


class TwigsTab(QtWidgets.QWidget):
    """
    List of twigs that have been decided on
    """
    refresh = QtCore.pyqtSignal(str)

    def __init__(self, common):
        super(TwigsTab, self).__init__()
        self.c = common

        self.c.log('TwigsTab', '__init__')

        # Keep track of the twig views
        self.twig_views = []

        # Label
        label = QtWidgets.QLabel("This is the data that we're collecting from your computer:")
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
        apply_button = QtWidgets.QPushButton("Apply Changes")
        apply_button.clicked.connect(self.clicked_apply_button)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(twigs_list, stretch=1)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def update_ui(self):
        self.c.log('TwigsTab', 'update_ui')

        # Remove all twigs
        for twig_view in self.twig_views:
            # Remove the twig view from the layout
            self.twigs_layout.removeWidget(twig_view)
            twig_view.close()

            # Remove it from the list of twig views
            self.twig_views.remove(twig_view)

        # Add decided twigs
        decided_twig_ids = self.c.settings.get_decided_twig_ids()
        for twig_id in reversed(decided_twig_ids):
            twig_view = TwigView(self.c, twig_id)
            self.twig_views.append(twig_view)
            self.twigs_layout.insertWidget(0, twig_view)

    def clicked_apply_button(self):
        self.c.log('TwigsTab', 'clicked_apply_button')

        for twig_view in self.twig_views:
            if twig_view.enabled_status == 'enabled':
                self.c.settings.enable_twig(twig_view.twig_id)
            elif twig_view.enabled_status == 'disabled':
                self.c.settings.disable_twig(twig_view.twig_id)
        self.c.settings.save()

        self.refresh.emit('twigs')
