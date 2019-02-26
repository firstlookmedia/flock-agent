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
        # Detect dark mode in macOS Mojova: https://stackoverflow.com/a/54701363
        if NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle') == 'Dark':
            self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray-dark.png'))
        else:
            self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray-light.png'))

        # Stylesheets
        self.css = {
            'header-label': """
            QLabel {
                font-size: 16px;
                margin-left: 10px;
            }
            """
        }
