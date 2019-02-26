# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from Foundation import NSUserDefaults


class GuiCommon(object):
    """
    Shared functionality across the GUI
    """
    def __init__(self, common):
        self.c = common

        # Preload icons
        self.icon = QtGui.QIcon(self.c.get_resource_path('images/icon.png'))
        if NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle') == 'Dark':
            self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray-dark.png'))
        else:
            self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray-light.png'))

        # Preload image labels
        logo_image = QtGui.QImage(self.c.get_resource_path("images/icon.png"))
        self.logo = QtWidgets.QLabel()
        self.logo.setPixmap(QtGui.QPixmap.fromImage(logo_image))

        # Stylesheets
        self.css = {
            'header-label': """
            QLabel {
                font-size: 16px;
                margin-left: 10px;
            }
            """
        }


class Alert(QtWidgets.QDialog):
    """
    A custom alert dialog
    """
    def __init__(self, common, message, contains_links=False):
        super(Alert, self).__init__()
        self.c = common

        self.setWindowTitle('Flock')
        self.setWindowIcon(self.c.gui.icon)
        self.setModal(True)
        self.setSizeGripEnabled(False)

        message_label = QtWidgets.QLabel(message)
        if contains_links:
            message_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            message_label.setOpenExternalLinks(True)

        message_layout = QtWidgets.QHBoxLayout()
        message_layout.addWidget(self.c.gui.logo)
        message_layout.addWidget(message_label)

        ok_button = QtWidgets.QPushButton('Ok')
        ok_button.clicked.connect(self.accept)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(message_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.exec_()
