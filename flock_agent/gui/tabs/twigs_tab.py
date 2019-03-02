# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..twigs import TwigView


class TwigsTab(QtWidgets.QWidget):
    """
    List of twigs, used for both the opt-in and data tabs
    """
    refresh = QtCore.pyqtSignal(str)

    def __init__(self, common, is_opt_in):
        """
        Set is_opt_in to True for the opt-in tab, and False for the data tab
        """
        super(TwigsTab, self).__init__()
        self.c = common
        if is_opt_in:
            self.mode = 'opt-in'
        else:
            self.mode = 'data'

        self.c.log('TwigsTab ({})'.format(self.mode), '__init__')

        # Keep track of the twig views
        self.twig_views = []

        # Label
        if self.mode == 'opt-in':
            label_text = "There is new data we'd like to collect from your computer. We recommend that enable all of it."
        else:
            label_text = "This is the data that we're collecting from your computer:"
        label = QtWidgets.QLabel(label_text)
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
        if self.mode == 'opt-in':
            enable_all_button = QtWidgets.QPushButton("Enable All")
            enable_all_button.setStyleSheet(self.c.gui.css['OptInTab enable_all_button'])
            enable_all_button.setFlat(True)
            enable_all_button.clicked.connect(self.clicked_enable_all_button)

        apply_button = QtWidgets.QPushButton("Apply Changes")
        apply_button.clicked.connect(self.clicked_apply_button)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        if self.mode == 'opt-in':
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
        self.c.log('TwigsTab ({})'.format(self.mode), 'update_ui')

        # Remove all twig views from the layout
        for twig_view in self.twig_views:
            # Remove the twig view from the layout
            self.twigs_layout.removeWidget(twig_view)
            twig_view.close()

        # Remove all twig views from the internal list
        for twig_view in self.twig_views:
            # Remove it from the list of twig views
            self.twig_views.remove(twig_view)

        # Get list of twig ids
        if self.mode == 'opt-in':
            twig_ids = self.c.settings.get_undecided_twig_ids()
        else:
            twig_ids = self.c.settings.get_decided_twig_ids()

        # Add them
        for twig_id in reversed(twig_ids):
            twig_view = TwigView(self.c, twig_id)
            self.twig_views.append(twig_view)
            self.twigs_layout.insertWidget(0, twig_view)

    def clicked_enable_all_button(self):
        if self.mode == 'opt-in':
            self.c.log('TwigsTab ({})'.format(self.mode), 'clicked_enable_all_button')

            for twig_id in self.c.settings.get_undecided_twig_ids():
                self.c.settings.enable_twig(twig_id)
            self.c.settings.save()

            self.refresh.emit(self.mode)

    def clicked_apply_button(self):
        self.c.log('TwigsTab ({})'.format(self.mode), 'clicked_apply_button')

        for twig_view in self.twig_views:
            if twig_view.enabled_status == 'enabled':
                self.c.settings.enable_twig(twig_view.twig_id)
            elif twig_view.enabled_status == 'disabled':
                self.c.settings.disable_twig(twig_view.twig_id)
        self.c.settings.save()

        self.refresh.emit(self.mode)
