# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..twigs import twigs


class TwigView(QtWidgets.QWidget):
    """
    The view of an individual twig
    """
    def __init__(self, common, twig_id):
        super(TwigView, self).__init__()
        self.c = common
        self.twig_id = twig_id

        self.c.log('TwigView', '__init__', twig_id)

        # Widgets
        name_label = QtWidgets.QLabel(twigs[twig_id]['name'])
        name_label.setStyleSheet(self.c.gui.css['TwigView name_label'])

        self.enabled_button = QtWidgets.QPushButton()
        self.enabled_button.setDefault(False)
        self.enabled_button.setFlat(True)
        self.enabled_button.setFixedWidth(64)
        self.enabled_button.setFixedHeight(32)
        self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-enabled.png')) )
        self.enabled_button.setIconSize(QtCore.QSize(64, 32))
        self.enabled_button.setStyleSheet(self.c.gui.css['TwigView enabled_button'])

        description_label = QtWidgets.QLabel(twigs[twig_id]['description'])
        description_label.setStyleSheet(self.c.gui.css['TwigView description_label'])
        description_label.setWordWrap(True)

        details_button = QtWidgets.QPushButton('Details')
        details_button.setFlat(True)
        details_button.setStyleSheet(self.c.gui.css['TwigView details_button'])

        # Layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(name_label, stretch=1)
        top_layout.addWidget(self.enabled_button)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(description_label, stretch=1)
        bottom_layout.addWidget(details_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)


class TwigsTab(QtWidgets.QWidget):
    """
    List of twigs
    """
    def __init__(self, common):
        super(TwigsTab, self).__init__()
        self.c = common

        self.c.log('TwigsTab', '__init__')

        # Label
        label = QtWidgets.QLabel("This is the data that we're collecting from your computer:")

        # List of twigs
        twigs_layout = QtWidgets.QVBoxLayout()
        for twig_id in twigs:
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
