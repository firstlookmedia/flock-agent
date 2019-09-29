# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from urllib.parse import urlparse

from ..api_client import FlockApiClient, PermissionDenied, BadStatusCode, \
    ResponseIsNotJson, RespondedWithError, InvalidResponse, ConnectionError
from ..common import Platform


if Platform.current() == Platform.MACOS:
    from Foundation import NSUserDefaults


class GuiCommon(object):
    """
    Shared functionality across the GUI
    """
    def __init__(self, common):
        self.c = common

        # Preload icons
        self.icon = QtGui.QIcon(self.c.get_resource_path('images/icon.png'))
        if Platform.current() == Platform.MACOS:
            if NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle') == 'Dark':
                self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray-dark.png'))
            else:
                self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray-light.png'))
        else:
            self.systray_icon = QtGui.QIcon(self.c.get_resource_path('images/systray.png'))

        # Stylesheets
        self.css = {
            'Onboarding label': """
                QLabel {
                    font-size: 16px;
                }
                """,

            'Onboarding url_label': """
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    font-family: monospace;
                }
                """,

            'Onboarding line_edit': """
                QLineEdit {
                    font-size: 16px;
                    padding: 5px;
                }
                """,

            'Onboarding radio_button': """
                QRadioButton {
                    font-size: 16px;
                }
                """,

            'Onboarding checkbox': """
                QCheckBox {
                    font-size: 16px;
                }
                """,

            'Onboarding brew_not_installed_label': """
                QLabel {
                    font-size: 16px;
                    color: #666666;
                }
                """,

            'MainWindow header_label': """
                QLabel {
                    font-size: 16px;
                    margin-left: 10px;
                }
                """,

            'HomebrewView package_names': """
                QLabel {
                    font-weight: bold;
                    padding-top: 10px;
                    padding-bottom: 10px;
                }
                """,

            'TwigView enabled_checkbox': """
                QCheckBox {
                    font-weight: bold;
                    font-size: 14px;
                    margin-right: 20px;
                }
                """,

            'TwigDialog name_label': """
                QLabel {
                    font-weight: bold;
                    font-size: 20px;
                }
                """,

            'TwigDialog description_label': """
                QLabel {
                    margin-bottom: 20px;
                }
                """,

            'TwigDialog interval_label': """
                QLabel {
                    font-style: italic;
                    color: #666666;
                }
                """,

            'TwigDialog osquery_label': """
                QLabel {
                    font-family: monospace;
                }
                """,

            'TwigDialog table_item_header': """
                QLabel {
                    font-family: monospace;
                    font-weight: bold;
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

            'SettingsTab group_box': """
                QGroupBox {
                    font-size: 14px;
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
                """,

            'link_button': """
                QPushButton {
                    color: #3461bc;
                    text-decoration: underline;
                    padding: 0 5px;
                    font-size: 12px;
                }
                """,
        }

    def register_server(self, server_url, name):
        # Validate server URL
        o = urlparse(server_url)
        if (o.scheme != 'http' and o.scheme != 'https') or (o.path != '' and o.path != '/') or \
            o.params != '' or o.query != '' or o.fragment != '':

            Alert(self.c, 'Invalid server URL').launch()
            return False

        # Save the server URL in settings
        self.c.settings.set('gateway_url', server_url)
        self.c.settings.save()

        # Try to register
        self.c.log('SettingsTab', 'server_button_clicked', 'registering with server')
        api_client = FlockApiClient(self.c)
        try:
            api_client.register(name)
            api_client.ping()
            return True
        except PermissionDenied:
            Alert(self.c, 'Permission denied').launch()
        except BadStatusCode as e:
            Alert(self.c, 'Bad status code: {}'.format(e)).launch()
        except ResponseIsNotJson:
            Alert(self.c, 'Server response is not JSON').launch()
        except RespondedWithError as e:
            Alert(self.c, 'Server error: {}'.format(e)).launch()
        except InvalidResponse:
            Alert(self.c, 'Server returned an invalid response').launch()
        except ConnectionError:
            Alert(self.c, 'Error connecting to server').launch()
        return False


class Alert(QtWidgets.QDialog):
    """
    A custom alert dialog
    """
    def __init__(self, common, message, contains_links=False, has_cancel_button=False, ok_text='Ok'):
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
        message_label.setWordWrap(True)
        if contains_links:
            message_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            message_label.setOpenExternalLinks(True)

        message_layout = QtWidgets.QHBoxLayout()
        message_layout.addWidget(logo)
        message_layout.addWidget(message_label)

        ok_button = QtWidgets.QPushButton(ok_text)
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


class HidableSpacer(QtWidgets.QWidget):
    """
    A custom widget that's used as spacing in a layout which can be shown or hidden
    """
    def __init__(self, size=10):
        super(HidableSpacer, self).__init__()
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)
