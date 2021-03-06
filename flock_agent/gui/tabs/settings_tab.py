# -*- coding: utf-8 -*-
import logging

from PyQt5 import QtCore, QtWidgets, QtGui

from ..gui_common import Alert, HidableSpacer
from ..daemon_client import DaemonNotRunningException, PermissionDeniedException
from ...common import Platform


class SettingsTab(QtWidgets.QWidget):
    """
    Settings
    """

    quit = QtCore.pyqtSignal()
    update_use_server = QtCore.pyqtSignal()

    STATUS_NOT_REGISTERED = 0
    STATUS_REGISTERED = 1

    def __init__(self, common):
        super(SettingsTab, self).__init__()
        self.c = common

        logger = logging.getLogger("SettingsTab.__init__")
        logger.debug("")

        # Use server checkbox
        self.use_server_checkbox = QtWidgets.QCheckBox(
            "Share data with a remote Flock server"
        )
        self.use_server_checkbox.stateChanged.connect(self.use_server_toggled)
        use_server_checkbox_spacer = HidableSpacer()

        # Name
        self.server_name_label = QtWidgets.QLabel("What's your name?")
        self.server_name_edit = QtWidgets.QLineEdit()
        self.server_name_edit.setPlaceholderText("Type your name here")

        # Server
        self.server_label = QtWidgets.QLabel()
        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setPlaceholderText("https://")
        self.server_url_label = QtWidgets.QLabel()
        self.server_url_label.setStyleSheet(
            self.c.gui.css["SettingsTab server_url_label"]
        )
        self.server_button = QtWidgets.QPushButton()
        self.server_button.setDefault(True)
        self.server_button.clicked.connect(self.server_button_clicked)

        server_url_layout = QtWidgets.QHBoxLayout()
        server_url_layout.addWidget(self.server_url_edit, stretch=1)
        server_url_layout.addWidget(self.server_url_label, stretch=1)
        server_url_layout.addWidget(self.server_button)

        server_layout = QtWidgets.QVBoxLayout()
        server_layout.addWidget(self.server_label)
        server_layout.addLayout(server_url_layout)

        # Automatically opt-in checkbox
        self.automatically_enable_twigs_checkbox = QtWidgets.QCheckBox(
            "Automatically opt-in to new data collection without asking me"
        )
        self.automatically_enable_twigs_checkbox.stateChanged.connect(
            self.automatically_enable_twigs_toggled
        )

        # Server group
        server_settings_layout = QtWidgets.QVBoxLayout()
        server_settings_layout.addWidget(self.server_name_label)
        server_settings_layout.addWidget(self.server_name_edit)
        server_settings_layout.addLayout(server_layout)
        server_settings_layout.addWidget(self.automatically_enable_twigs_checkbox)
        self.server_settings_group = QtWidgets.QGroupBox("Server settings")
        self.server_settings_group.setStyleSheet(
            self.c.gui.css["SettingsTab group_box"]
        )
        self.server_settings_group.setLayout(server_settings_layout)
        self.server_settings_group_spacer = HidableSpacer()

        if Platform.current() == Platform.MACOS:
            # Autoupdate homebrew checkbox
            self.homebrew_update_prompt_checkbox = QtWidgets.QCheckBox(
                "Prompt me when Homebrew updates are available"
            )
            self.homebrew_update_prompt_checkbox.stateChanged.connect(
                self.homebrew_update_prompt_toggled
            )

            # Autoupdate homebrew cask checkbox
            self.homebrew_autoupdate_checkbox = QtWidgets.QCheckBox(
                "Automatically install Homebrew updates (if they don't require a password)"
            )
            self.homebrew_autoupdate_checkbox.stateChanged.connect(
                self.homebrew_autoupdate_toggled
            )

            # Homebrew group
            homebrew_settings_layout = QtWidgets.QVBoxLayout()
            homebrew_settings_layout.addWidget(self.homebrew_update_prompt_checkbox)
            homebrew_settings_layout.addWidget(self.homebrew_autoupdate_checkbox)
            homebrew_settings_group = QtWidgets.QGroupBox("Homebrew settings")
            homebrew_settings_group.setStyleSheet(
                self.c.gui.css["SettingsTab group_box"]
            )
            homebrew_settings_group.setLayout(homebrew_settings_layout)
            homebrew_settings_group_spacer = HidableSpacer()

        # Buttons
        quit_button = QtWidgets.QPushButton("Quit Flock Agent")
        quit_button.clicked.connect(self.quit_clicked)
        quit_button.setStyleSheet(self.c.gui.css["SettingsTab quit_button"])
        quit_button.setFlat(True)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(quit_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.use_server_checkbox)
        layout.addWidget(use_server_checkbox_spacer)
        layout.addWidget(self.server_settings_group)
        layout.addWidget(
            self.server_settings_group_spacer
        )  # custom spacing widget, so we can hide it
        if Platform.current() == Platform.MACOS:
            layout.addWidget(homebrew_settings_group)
            layout.addWidget(homebrew_settings_group_spacer)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.update_ui()

    def update_ui(self):
        logger = logging.getLogger("SettingsTab.update_ui")
        logger.debug("")

        try:
            # Determine server status
            if self.c.daemon.get("gateway_url") and self.c.daemon.get("gateway_token"):
                self.status = self.STATUS_REGISTERED
            else:
                self.status = self.STATUS_NOT_REGISTERED

            # Use server checkbox
            if self.c.daemon.get("use_server"):
                self.use_server_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
                self.server_settings_group.show()
                self.server_settings_group_spacer.show()
            else:
                self.use_server_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
                self.server_settings_group.hide()
                self.server_settings_group_spacer.hide()

            # Not registered yet
            self.server_label.show()
            if self.status == self.STATUS_NOT_REGISTERED:
                self.server_name_label.show()
                self.server_name_edit.show()
                self.server_label.setText(
                    "What's the address of the server you will send data to?"
                )
                self.server_url_edit.show()
                self.server_url_label.hide()
                self.server_button.show()
                self.server_button.setEnabled(True)
                self.server_button.setText("Connect")

            elif self.status == self.STATUS_REGISTERED:
                self.server_name_label.hide()
                self.server_name_edit.hide()
                self.server_label.setText("You're sending data to this server:")
                self.server_url_edit.hide()
                self.server_url_label.setText(self.c.daemon.get("gateway_url"))
                self.server_url_label.show()
                self.server_button.hide()

            # Automatically opt-in checkbox
            self.automatically_enable_twigs_checkbox.show()
            if self.c.daemon.get("automatically_enable_twigs"):
                self.automatically_enable_twigs_checkbox.setCheckState(
                    QtCore.Qt.CheckState.Checked
                )
            else:
                self.automatically_enable_twigs_checkbox.setCheckState(
                    QtCore.Qt.CheckState.Unchecked
                )

            if Platform.current() == Platform.MACOS:
                # Homebrew update prompt checkbox
                if self.c.gui.settings.get("homebrew_update_prompt"):
                    self.homebrew_update_prompt_checkbox.setCheckState(
                        QtCore.Qt.CheckState.Checked
                    )
                else:
                    self.homebrew_update_prompt_checkbox.setCheckState(
                        QtCore.Qt.CheckState.Unchecked
                    )

                # Homebrew autoupdate checkbox
                if self.c.gui.settings.get("homebrew_autoupdate"):
                    self.homebrew_autoupdate_checkbox.setCheckState(
                        QtCore.Qt.CheckState.Checked
                    )
                else:
                    self.homebrew_autoupdate_checkbox.setCheckState(
                        QtCore.Qt.CheckState.Unchecked
                    )
        except DaemonNotRunningException:
            self.c.gui.daemon_not_running()
        except PermissionDeniedException:
            self.c.gui.daemon_permission_denied()

    def server_button_clicked(self):
        logger = logging.getLogger("SettingsTab.server_button_clicked")
        logger.debug("")

        if self.status == self.STATUS_NOT_REGISTERED:
            self.server_button.setEnabled(False)
            self.server_button.setText("Registering...")

            # Try registering
            name = self.server_name_edit.text()
            server_url = self.server_url_edit.text()
            try:
                self.c.daemon.register_server(server_url, name)
            except DaemonNotRunningException:
                self.c.gui.daemon_not_running()
                return
            except PermissionDeniedException:
                self.c.gui.daemon_permission_denied()
                return

        self.update_ui()

    def use_server_toggled(self):
        logger = logging.getLogger("SettingsTab.use_server_toggled")
        logger.debug("")
        is_checked = (
            self.use_server_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        )
        try:
            self.c.daemon.set("use_server", is_checked)
        except DaemonNotRunningException:
            self.c.gui.daemon_not_running()
            return
        except PermissionDeniedException:
            self.c.gui.daemon_permission_denied()
            return
        self.update_use_server.emit()
        self.update_ui()

    def automatically_enable_twigs_toggled(self):
        logger = logging.getLogger("SettingsTab.automatically_enable_twigs_toggled")
        logger.debug("")
        is_checked = (
            self.automatically_enable_twigs_checkbox.checkState()
            == QtCore.Qt.CheckState.Checked
        )
        try:
            self.c.daemon.set("automatically_enable_twigs", is_checked)
        except DaemonNotRunningException:
            self.c.gui.daemon_not_running()
        except PermissionDeniedException:
            self.c.gui.daemon_permission_denied()

    def homebrew_update_prompt_toggled(self):
        logger = logging.getLogger("SettingsTab.homebrew_update_prompt_toggled")
        logger.debug("")
        is_checked = (
            self.homebrew_update_prompt_checkbox.checkState()
            == QtCore.Qt.CheckState.Checked
        )
        self.c.gui.settings.set("homebrew_update_prompt", is_checked)
        self.c.gui.settings.save()

    def homebrew_autoupdate_toggled(self):
        logger = logging.getLogger("SettingsTab.homebrew_autoupdate_toggled")
        logger.debug("")
        is_checked = (
            self.homebrew_autoupdate_checkbox.checkState()
            == QtCore.Qt.CheckState.Checked
        )
        self.c.gui.settings.set("homebrew_autoupdate", is_checked)
        self.c.gui.settings.save()

    def quit_clicked(self):
        logger = logging.getLogger("SettingsTab.quit_clicked")
        logger.debug("")
        self.quit.emit()
