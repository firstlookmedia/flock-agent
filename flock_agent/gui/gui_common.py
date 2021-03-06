# -*- coding: utf-8 -*-
import logging
import subprocess

from PyQt5 import QtCore, QtWidgets, QtGui

from .settings import Settings

from ..common import Platform

if Platform.current() == Platform.MACOS:
    from Foundation import NSUserDefaults


class GuiCommon:
    """
    Shared functionality across the GUI
    """

    def __init__(self, common, app):
        self.c = common
        self.app = app  # the Qt app

        # Load settings
        self.settings = Settings(self.c)

        # Preload icons
        self.icon = QtGui.QIcon(self.c.get_resource_path("images/icon.png"))
        if Platform.current() == Platform.MACOS:
            self.systray_icon_dark = QtGui.QIcon(
                self.c.get_resource_path("images/systray-dark.png")
            )
            self.systray_icon_light = QtGui.QIcon(
                self.c.get_resource_path("images/systray-light.png")
            )
        else:
            self.systray_icon = QtGui.QIcon(
                self.c.get_resource_path("images/systray.png")
            )

        # Stylesheets
        self.css = {
            "Onboarding label": """
                QLabel {
                    font-size: 16px;
                }
                """,
            "Onboarding url_label": """
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    font-family: monospace;
                }
                """,
            "Onboarding line_edit": """
                QLineEdit {
                    font-size: 16px;
                    padding: 5px;
                }
                """,
            "Onboarding radio_button": """
                QRadioButton {
                    font-size: 16px;
                }
                """,
            "Onboarding checkbox": """
                QCheckBox {
                    font-size: 16px;
                }
                """,
            "Onboarding brew_not_installed_label": """
                QLabel {
                    font-size: 16px;
                    color: #666666;
                }
                """,
            "MainWindow header_label": """
                QLabel {
                    font-size: 16px;
                    margin-left: 10px;
                }
                """,
            "HomebrewView package_names": """
                QLabel {
                    font-weight: bold;
                    padding-top: 10px;
                    padding-bottom: 10px;
                }
                """,
            "TwigView enabled_checkbox": """
                QCheckBox {
                    font-weight: bold;
                    font-size: 14px;
                    margin-right: 20px;
                }
                """,
            "TwigDialog name_label": """
                QLabel {
                    font-weight: bold;
                    font-size: 20px;
                }
                """,
            "TwigDialog description_label": """
                QLabel {
                    margin-bottom: 20px;
                }
                """,
            "TwigDialog interval_label": """
                QLabel {
                    font-style: italic;
                    color: #666666;
                }
                """,
            "TwigDialog osquery_label": """
                QLabel {
                    font-family: monospace;
                }
                """,
            "TwigDialog table_item_header": """
                QLabel {
                    font-family: monospace;
                    font-weight: bold;
                }
                """,
            "OptInTab enable_all_button": """
                QPushButton {
                    color: #ffffff;
                    background-color: #2e8e2a;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 5px;
                    padding: 5px 10px 5px 10px;
                }
                """,
            "SettingsTab group_box": """
                QGroupBox {
                    font-size: 14px;
                }
            """,
            "SettingsTab server_url_label": """
                QLabel {
                    font-family: monospace;
                    font-weight: bold;
                }
            """,
            "SettingsTab quit_button": """
                QPushButton {
                    color: #ffffff;
                    background-color: #ea2a2a;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 5px 10px 5px 10px;
                }
                """,
            "link_button": """
                QPushButton {
                    color: #3461bc;
                    text-decoration: underline;
                    padding: 0 5px;
                    font-size: 12px;
                }
                """,
        }

    def daemon_not_running(self):
        """
        Handling when the daemon isn't running
        """
        logger = logging.getLogger("GuiCommon.daemon_not_running")
        logger.debug("")
        message = "<b>Flock Agent daemon is not running.</b><br><br>Click Ok to try starting it in the background. You will have to type your login password."
        if Alert(self.c, message, has_cancel_button=True).launch():
            logger.info("enabling background daemon")
            if Platform.current() == Platform.UNKNOWN:
                # Unknown platform
                message = "<b>Flock Agent doesn't recognize your operating system.</b><br><br>Sorry, I don't know how to start the daemon."
                Alert(self.c, message).launch()
            else:
                if Platform.current() == Platform.MACOS:
                    # Enable service
                    p = subprocess.run(
                        [
                            "/usr/bin/osascript",
                            "-e",
                            'do shell script "{}" with administrator privileges'.format(
                                self.c.get_resource_path(
                                    "autostart/macos/enable_daemon"
                                )
                            ),
                        ]
                    )
                elif Platform.current() == Platform.LINUX:
                    # Enable service
                    p = subprocess.run(
                        [
                            "/usr/bin/pkexec",
                            self.c.get_resource_path("autostart/linux/enable_daemon"),
                        ]
                    )

                if p.returncode == 0:
                    # Tell user to restart
                    message = "<b>Restart Flock Agent.</b><br><br>The daemon should be running now. Please open Flock Agent again."
                    Alert(self.c, message).launch()
                else:
                    # Failed
                    message = "<b>Starting background daemon failed.</b>"
                    Alert(self.c, message).launch()

        # Quit the app
        self.app.quit()

    def daemon_permission_denied(self):
        """
        Handling when permission to use the daemon is denied
        """
        logger = logging.getLogger("GuiCommon.daemon_permission_denied")
        logger.debug("")
        message = "<b>Permission denied.</b><br><br>Sorry, you must have admin rights on your computer to configure Flock Agent."
        Alert(self.c, message).launch()
        # Quit the app
        self.app.exit()


class Alert(QtWidgets.QDialog):
    """
    A custom alert dialog
    """

    def __init__(
        self,
        common,
        message,
        contains_links=False,
        has_cancel_button=False,
        ok_text="Ok",
    ):
        super(Alert, self).__init__()
        self.c = common

        self.setWindowTitle("Flock")
        self.setWindowIcon(self.c.gui.icon)
        self.setModal(True)
        self.setSizeGripEnabled(False)

        flags = (
            QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setWindowFlags(flags)

        logo = QtWidgets.QLabel()
        logo.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(self.c.get_resource_path("images/icon.png"))
            )
        )

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
            cancel_button = QtWidgets.QPushButton("Cancel")
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
