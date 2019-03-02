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

        # Set the initial enabled status from settings
        self.enabled_status = self.get_twig()['enabled']

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
        self.enabled_button.clicked.connect(self.clicked_enabled_button)

        description_label = QtWidgets.QLabel(twigs[twig_id]['description'])
        description_label.setWordWrap(True)

        details_button = QtWidgets.QPushButton('Details')
        details_button.setFlat(True)
        details_button.setStyleSheet(self.c.gui.css['TwigView details_button'])
        details_button.clicked.connect(self.clicked_details_button)

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
        if self.enabled_status == 'enabled':
            self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-enabled.png')) )
        elif self.enabled_status == 'disabled':
            self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-disabled.png')) )
        else:
            self.enabled_button.setIcon( QtGui.QIcon(self.c.get_resource_path('images/switch-undecided.png')) )

    def clicked_enabled_button(self):
        if self.enabled_status == 'undecided':
            self.enabled_status = 'enabled'
        elif self.enabled_status == 'enabled':
            self.enabled_status = 'disabled'
        elif self.enabled_status == 'disabled':
            self.enabled_status = 'enabled'
        self.update_ui()

    def clicked_details_button(self):
        TwigDialog(self.c, self.twig_id)

    def get_twig(self):
        return self.c.settings.get_twig(self.twig_id)


class TwigDialog(QtWidgets.QDialog):
    """
    A dialog box showing details about a twig
    """
    def __init__(self, common, twig_id):
        super(TwigDialog, self).__init__()
        self.c = common
        self.twig_id = twig_id

        self.setWindowTitle('Details of: {}'.format(twigs[self.twig_id]['name']))
        self.setWindowIcon(self.c.gui.icon)
        self.setModal(True)

        name_label = QtWidgets.QLabel(twigs[twig_id]['name'])
        name_label.setStyleSheet(self.c.gui.css['TwigDialog name_label'])

        description_label = QtWidgets.QLabel(twigs[twig_id]['description'])
        description_label.setWordWrap(True)

        interval_label = QtWidgets.QLabel(self.get_interval_string())
        interval_label.setStyleSheet(self.c.gui.css['TwigDialog interval_label'])

        ok_button = QtWidgets.QPushButton('Ok')
        ok_button.clicked.connect(self.accept)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(description_label)
        layout.addWidget(interval_label)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.exec_()

    def get_interval_string(self):
        seconds = twigs[self.twig_id]['interval']
        minutes = 0
        hours = 0
        if seconds > 60:
            minutes = seconds // 60
            seconds = seconds % 60
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60

        text = "Runs every "
        parts = []
        if hours > 0:
            parts.append("{} hours".format(hours))
        if minutes > 0:
            parts.append("{} minutes".format(minutes))
        if seconds > 0:
            parts.append("{} seconds".format(seconds))
        text += ", ".join(parts)
        return text

    def get_twig(self):
        return self.c.settings.get_twig(self.twig_id)
