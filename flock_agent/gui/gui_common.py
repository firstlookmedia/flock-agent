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

        # Stylesheets
        self.css = {
            'MainWindow header_label': """
                QLabel {
                    font-size: 16px;
                    margin-left: 10px;
                }
                """,

            'TwigView name_label': """
                QLabel {
                    font-weight: bold;
                    font-size: 16px;
                }
                """,

            'TwigView enabled_button': """
                QPushButton {
                    margin: 0;
                    padding: 0;
                }
                """,

            'TwigView details_button': """
                QPushButton {
                    color: #3461bc;
                    text-decoration: underline;
                    padding: 5px;
                    font-size: 12px;
                }
                """,

            'TwigDialog name_label': """
                QLabel {
                    font-weight: bold;
                    font-size: 16px;
                }
                """,

            'TwigDialog interval_label': """
                QLabel {
                    font-style: italic;
                    color: #666666;
                }
                """,

            'OptInTab enable_all_button': """
                QPushButton {
                    color: #ffffff;
                    background-color: #2e8e2a;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 5px;
                    padding: 5px 10px 5px 10px;
                }
                """,

            'SettingsTab server_url_label': """
                QLabel {
                    font-family: monospace;
                    font-weight: bold;
                }
            """,

            'SettingsTab quit_button': """
                QPushButton {
                    color: #ffffff;
                    background-color: #ea2a2a;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 5px 10px 5px 10px;
                }
                """
        }


class Alert(QtWidgets.QDialog):
    """
    A custom alert dialog
    """
    def __init__(self, common, message, contains_links=False, has_cancel_button=False):
        super(Alert, self).__init__()
        self.c = common

        self.setWindowTitle('Flock')
        self.setWindowIcon(self.c.gui.icon)
        self.setModal(True)
        self.setSizeGripEnabled(False)

        flags = QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | \
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint | \
            QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/icon.png"))))

        message_label = QtWidgets.QLabel(message)
        if contains_links:
            message_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            message_label.setOpenExternalLinks(True)

        message_layout = QtWidgets.QHBoxLayout()
        message_layout.addWidget(logo)
        message_layout.addWidget(message_label)

        ok_button = QtWidgets.QPushButton('Ok')
        ok_button.clicked.connect(self.accept)

        if has_cancel_button:
            cancel_button = QtWidgets.QPushButton('Cancel')
            cancel_button.clicked.connect(self.reject)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        if has_cancel_button:
            buttons_layout.addWidget(cancel_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(message_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def launch(self):
        return self.exec_() == QtWidgets.QDialog.Accepted
