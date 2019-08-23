# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..gui_common import Alert, HidableSpacer


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

        self.c.log('SettingsTab', '__init__')

        # Determine server status
        if self.c.settings.get('gateway_url') and self.c.settings.get('gateway_token'):
            self.status = self.STATUS_REGISTERED
        else:
            self.status = self.STATUS_NOT_REGISTERED

        # Use server checkbox
        self.use_server_checkbox = QtWidgets.QCheckBox("Share data with a remote Flock server")
        self.use_server_checkbox.stateChanged.connect(self.use_server_toggled)
        use_server_checkbox_spacer = HidableSpacer()

        # Server
        self.server_label = QtWidgets.QLabel()
        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setPlaceholderText("https://")
        self.server_url_label = QtWidgets.QLabel()
        self.server_url_label.setStyleSheet(self.c.gui.css['SettingsTab server_url_label'])
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
        self.automatically_enable_twigs_checkbox = QtWidgets.QCheckBox("Automatically opt-in to new data collection without asking me")
        self.automatically_enable_twigs_checkbox.stateChanged.connect(self.automatically_enable_twigs_toggled)

        # Server group
        server_settings_layout = QtWidgets.QVBoxLayout()
        server_settings_layout.addLayout(server_layout)
        server_settings_layout.addWidget(self.automatically_enable_twigs_checkbox)
        self.server_settings_group = QtWidgets.QGroupBox("Server settings")
        self.server_settings_group.setStyleSheet(self.c.gui.css['SettingsTab group_box'])
        self.server_settings_group.setLayout(server_settings_layout)
        self.server_settings_group_spacer = HidableSpacer()

        # Autoupdate homebrew checkbox
        self.homebrew_update_prompt_checkbox = QtWidgets.QCheckBox("Prompt when Homebrew updates are available")
        self.homebrew_update_prompt_checkbox.stateChanged.connect(self.homebrew_update_prompt_toggled)

        # Autoupdate homebrew cask checkbox
        self.homebrew_autoupdate_checkbox = QtWidgets.QCheckBox("Automatically install Homebrew updates (if they don't require a password)")
        self.homebrew_autoupdate_checkbox.stateChanged.connect(self.homebrew_autoupdate_toggled)

        # Homebrew group
        homebrew_settings_layout = QtWidgets.QVBoxLayout()
        homebrew_settings_layout.addWidget(self.homebrew_update_prompt_checkbox)
        homebrew_settings_layout.addWidget(self.homebrew_autoupdate_checkbox)
        homebrew_settings_group = QtWidgets.QGroupBox("Homebrew settings")
        homebrew_settings_group.setStyleSheet(self.c.gui.css['SettingsTab group_box'])
        homebrew_settings_group.setLayout(homebrew_settings_layout)
        homebrew_settings_group_spacer = HidableSpacer()

        # Buttons
        quit_button = QtWidgets.QPushButton('Quit Flock Agent')
        quit_button.clicked.connect(self.quit_clicked)
        quit_button.setStyleSheet(self.c.gui.css['SettingsTab quit_button'])
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
        layout.addWidget(self.server_settings_group_spacer) # custom spacing widget, so we can hide it
        layout.addWidget(homebrew_settings_group)
        layout.addWidget(homebrew_settings_group_spacer)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.update_ui()

    def update_ui(self):
        self.c.log('SettingsTab', 'update_ui')

        # Use server checkbox
        if self.c.settings.get('use_server'):
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
            self.server_label.setText('What\'s the address of the server you will send data to?')
            self.server_url_edit.show()
            self.server_url_label.hide()
            self.server_button.show()
            self.server_button.setEnabled(True)
            self.server_button.setText('Connect')

        elif self.status == self.STATUS_REGISTERED:
            self.server_label.setText('You\'re sending data to this server:')
            self.server_url_edit.hide()
            self.server_url_label.setText(self.c.settings.get('gateway_url'))
            self.server_url_label.show()
            self.server_button.hide()

        # Automatically opt-in checkbox
        self.automatically_enable_twigs_checkbox.show()
        if self.c.settings.get('automatically_enable_twigs'):
            self.automatically_enable_twigs_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.automatically_enable_twigs_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        # Homebrew update prompt checkbox
        if self.c.settings.get('homebrew_update_prompt'):
            self.homebrew_update_prompt_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.homebrew_update_prompt_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        # Homebrew autoupdate checkbox
        if self.c.settings.get('homebrew_autoupdate'):
            self.homebrew_autoupdate_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.homebrew_autoupdate_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def server_button_clicked(self):
        self.c.log('SettingsTab', 'server_button_clicked')

        if self.status == self.STATUS_NOT_REGISTERED:
            self.server_button.setEnabled(False)
            self.server_button.setText('Registering...')

            # Try registering the URL
            server_url = self.server_url_edit.text()
            if self.c.gui.register_server(server_url):
                # Save the server URL in settings
                self.c.settings.set('gateway_url', server_url)
                self.c.settings.save()

        self.update_ui()

    def use_server_toggled(self):
        self.c.log('SettingsTab', 'use_server_toggled')
        is_checked = self.use_server_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.c.settings.set('use_server', is_checked)
        self.c.settings.save()
        self.update_use_server.emit()
        self.update_ui()

    def automatically_enable_twigs_toggled(self):
        self.c.log('SettingsTab', 'automatically_enable_twigs_toggled')
        is_checked = self.automatically_enable_twigs_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.c.settings.set('automatically_enable_twigs', is_checked)
        self.c.settings.save()

    def homebrew_update_prompt_toggled(self):
        self.c.log('SettingsTab', 'homebrew_update_prompt_toggled')
        is_checked = self.homebrew_update_prompt_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.c.settings.set('homebrew_update_prompt', is_checked)
        self.c.settings.save()

    def homebrew_autoupdate_toggled(self):
        self.c.log('SettingsTab', 'homebrew_autoupdate_toggled')
        is_checked = self.homebrew_autoupdate_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.c.settings.set('homebrew_autoupdate', is_checked)
        self.c.settings.save()

    def quit_clicked(self):
        self.c.log('SettingsTab', 'quit_clicked')
        self.quit.emit()
