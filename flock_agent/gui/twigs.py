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

        self.update_ui()

    def update_ui(self):
        twig = self.get_twig()
        if twig['enabled'] == 'enabled':
            self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-enabled.png')) )
        elif twig['enabled'] == 'disabled':
            self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-disabled.png')) )
        else:
            self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-undecided.png')) )

    def get_twig(self):
        return self.c.settings.get_twig(self.twig_id)
