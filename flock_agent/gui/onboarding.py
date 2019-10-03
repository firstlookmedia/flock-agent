# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore, QtWidgets, QtGui

from ..common import Platform


class Pages:
    SERVER = 1
    DATA = 2
    HOMEBREW = 3
    APPLET = 4


class ServerPage(QtWidgets.QWizardPage):
    def __init__(self, common):
        super(ServerPage, self).__init__()
        self.c = common

        self.setTitle("Welcome to Flock")

        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(self.c.get_resource_path("images/onboarding-page1.png"))
        )
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, pixmap)

        # Instructions
        instructions_label = QtWidgets.QLabel(
            "Flock can help secure your computer whether you're an individual or part of an organization."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet(self.c.gui.css["Onboarding label"])

        # Use server
        self.use_server_no = QtWidgets.QRadioButton("I'm an individual")
        self.use_server_no.toggled.connect(self.use_server_toggled)
        self.use_server_no.setStyleSheet(self.c.gui.css["Onboarding radio_button"])
        self.use_server_yes = QtWidgets.QRadioButton(
            "I'm part of an organization and want to share data with my security team"
        )
        self.use_server_yes.toggled.connect(self.use_server_toggled)
        self.use_server_yes.setStyleSheet(self.c.gui.css["Onboarding radio_button"])

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(instructions_label)
        layout.addSpacing(20)
        layout.addWidget(self.use_server_no)
        layout.addSpacing(20)
        layout.addWidget(self.use_server_yes)
        self.setLayout(layout)

    def nextId(self):
        if self.use_server_yes.isChecked():
            return Pages.DATA
        else:
            if Platform.current() == Platform.MACOS:
                return Pages.HOMEBREW
            else:
                return Pages.APPLET

    def isComplete(self):
        return self.use_server_yes.isChecked() or self.use_server_no.isChecked()

    def use_server_toggled(self):
        self.completeChanged.emit()


class DataPage(QtWidgets.QWizardPage):
    def __init__(self, common):
        super(DataPage, self).__init__()
        self.c = common

        self.is_registered = False

        self.setTitle("Sharing data with your security team")

        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(self.c.get_resource_path("images/onboarding-page2.png"))
        )
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, pixmap)

        # Instructions
        instructions_label = QtWidgets.QLabel(
            "Flock sends data to a server controlled by your security team, like what version of macOS you're using, what apps and browser extensions are installed, and what programs start automatically. Flock does not share your documents, browser history, or other private data."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet(self.c.gui.css["Onboarding label"])

        # Name
        name_label = QtWidgets.QLabel("What's your name?")
        name_label.setStyleSheet(self.c.gui.css["Onboarding label"])
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Type your name here")
        self.name_edit.setStyleSheet(self.c.gui.css["Onboarding line_edit"])

        # Server
        self.server_label = QtWidgets.QLabel(
            "What's the address of the server you will send data to?"
        )
        self.server_label.setStyleSheet(self.c.gui.css["Onboarding label"])
        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setPlaceholderText("https://")
        self.server_url_edit.setStyleSheet(self.c.gui.css["Onboarding line_edit"])
        self.server_url_label = QtWidgets.QLabel()
        self.server_url_label.setStyleSheet(self.c.gui.css["Onboarding url_label"])
        self.server_url_label.hide()
        self.server_button = QtWidgets.QPushButton("Connect")
        self.server_button.setDefault(True)
        self.server_button.setEnabled(True)
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
        self.automatically_enable_twigs_checkbox.setStyleSheet(
            self.c.gui.css["Onboarding checkbox"]
        )

        # Pre-check this box, to encourage the user to opt-in -- even though the setting itself defaults as False
        # This way if they manually uncheck, they still have a chance to opt-in before sending any data
        self.automatically_enable_twigs_checkbox.setCheckState(
            QtCore.Qt.CheckState.Checked
        )

        automatically_enable_twigs_label = QtWidgets.QLabel(
            "If you don't want to automatically opt-in, you must choose which types of data you want to share with your security team. If a Flock update contains new types of data, you will be asked if you want to opt-in to these as well. It's recommended that you opt-in to sharing everything."
        )
        automatically_enable_twigs_label.setWordWrap(True)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(instructions_label)
        layout.addSpacing(20)
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)
        layout.addSpacing(20)
        layout.addLayout(server_layout)
        layout.addSpacing(20)
        layout.addWidget(self.automatically_enable_twigs_checkbox)
        layout.addWidget(automatically_enable_twigs_label)
        layout.addStretch()
        self.setLayout(layout)

    def isComplete(self):
        return self.is_registered

    def server_button_clicked(self):
        self.c.log("DataPage", "server_button_clicked")

        self.server_button.setEnabled(False)
        self.server_button.setText("Registering...")
        self.name_edit.setEnabled(False)

        # Try registering the URL
        name = self.name_edit.text()
        server_url = self.server_url_edit.text()
        if self.c.gui.register_server(server_url, name):
            self.server_label.setText(
                "Success! Flock will share data with this server:"
            )
            self.server_url_edit.hide()
            self.server_url_label.setText(server_url)
            self.server_url_label.show()
            self.server_button.hide()

            self.is_registered = True
            self.completeChanged.emit()

        else:
            self.server_button.setEnabled(True)
            self.server_button.setText("Connect")
            self.name_edit.setEnabled(True)


class HomebrewPage(QtWidgets.QWizardPage):
    def __init__(self, common):
        super(HomebrewPage, self).__init__()
        self.c = common

        self.setTitle("Keeping your software up-to-date")

        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(self.c.get_resource_path("images/onboarding-page3.png"))
        )
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, pixmap)

        # Instructions
        instructions_label = QtWidgets.QLabel(
            "Flock helps you keep macOS apps and command line programs that were installed through Homebrew up-to-date."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet(self.c.gui.css["Onboarding label"])

        # Homebrew not installed warning
        brew_not_installed_label = QtWidgets.QLabel(
            "You currently don't have Homebrew installed, so these settings won't affect you. If you'd like to use Homebrew, you can install it by following the instructions at <a href='https://brew.sh'>https://brew.sh</a>."
        )
        brew_not_installed_label.setWordWrap(True)
        brew_not_installed_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction
        )
        brew_not_installed_label.setOpenExternalLinks(True)
        brew_not_installed_label.setStyleSheet(
            self.c.gui.css["Onboarding brew_not_installed_label"]
        )

        # Autoupdate homebrew checkbox
        self.homebrew_update_prompt_checkbox = QtWidgets.QCheckBox(
            "Prompt me when Homebrew updates are available"
        )
        self.homebrew_update_prompt_checkbox.setStyleSheet(
            self.c.gui.css["Onboarding checkbox"]
        )
        if self.c.gui.settings.get("homebrew_update_prompt"):
            self.homebrew_update_prompt_checkbox.setCheckState(
                QtCore.Qt.CheckState.Checked
            )
        else:
            self.homebrew_update_prompt_checkbox.setCheckState(
                QtCore.Qt.CheckState.Unchecked
            )

        # Autoupdate homebrew cask checkbox
        self.homebrew_autoupdate_checkbox = QtWidgets.QCheckBox(
            "Automatically install Homebrew updates (if they don't require a password)"
        )
        self.homebrew_autoupdate_checkbox.setStyleSheet(
            self.c.gui.css["Onboarding checkbox"]
        )
        if self.c.gui.settings.get("homebrew_autoupdate"):
            self.homebrew_autoupdate_checkbox.setCheckState(
                QtCore.Qt.CheckState.Checked
            )
        else:
            self.homebrew_autoupdate_checkbox.setCheckState(
                QtCore.Qt.CheckState.Unchecked
            )

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(instructions_label)
        layout.addSpacing(20)
        if not os.path.exists("/usr/local/bin/brew"):
            layout.addWidget(brew_not_installed_label)
            layout.addSpacing(20)
        layout.addWidget(self.homebrew_update_prompt_checkbox)
        layout.addSpacing(20)
        layout.addWidget(self.homebrew_autoupdate_checkbox)
        self.setLayout(layout)


class AppletPage(QtWidgets.QWizardPage):
    def __init__(self, common):
        super(AppletPage, self).__init__()
        self.c = common

        self.setTitle("Accessing Flock")

        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(self.c.get_resource_path("images/onboarding-page4.png"))
        )
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, pixmap)

        label = QtWidgets.QLabel(
            "If you want to check on the health of your computer or change any Flock settings, click the bird icon in your system tray."
        )
        label.setWordWrap(True)
        label.setStyleSheet(self.c.gui.css["Onboarding label"])

        # TODO: make separate macOS/Linux screenshots for this icon
        systray_image = QtWidgets.QLabel()
        systray_image.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(self.c.get_resource_path("images/onboarding-systray.png"))
            )
        )

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addSpacing(20)
        layout.addWidget(systray_image)
        self.setLayout(layout)


class Onboarding(QtWidgets.QWizard):
    """
    The onboarding assistant, for the first run of Flock Agent
    """

    finished = QtCore.pyqtSignal()

    def __init__(self, common):
        super(Onboarding, self).__init__()
        self.c = common
        self.c.log("Onboarding", "__init__")

        self.setWindowTitle("Configuring Flock")
        self.setMinimumWidth(790)
        self.setMinimumHeight(540)

        self.setWizardStyle(QtWidgets.QWizard.MacStyle)

        self.server_page = ServerPage(self.c)
        self.data_page = DataPage(self.c)
        if Platform.current() == Platform.MACOS:
            self.homebrew_page = HomebrewPage(self.c)
        self.applet_page = AppletPage(self.c)

        self.setPage(Pages.SERVER, self.server_page)
        self.setPage(Pages.DATA, self.data_page)
        if Platform.current() == Platform.MACOS:
            self.setPage(Pages.HOMEBREW, self.homebrew_page)
        self.setPage(Pages.APPLET, self.applet_page)

    def done(self, result):
        super(Onboarding, self).done(result)

        # Save settings
        use_server = self.server_page.use_server_yes.isChecked()
        self.c.settings.set("use_server", use_server)
        if use_server:
            # gateway_url and gateway_token were saved when registering
            automatically_enable_twigs = (
                self.data_page.automatically_enable_twigs_checkbox.checkState()
                == QtCore.Qt.CheckState.Checked
            )
            self.c.settings.set(
                "automatically_enable_twigs", automatically_enable_twigs
            )

            # Automatically enable the twigs, if checkbox was checked
            if automatically_enable_twigs:
                for twig_id in self.c.settings.get_undecided_twig_ids():
                    self.c.settings.enable_twig(twig_id)

        if Platform.current() == Platform.MACOS:
            homebrew_update_prompt = (
                self.homebrew_page.homebrew_update_prompt_checkbox.checkState()
                == QtCore.Qt.CheckState.Checked
            )
            self.c.gui.settings.set("homebrew_update_prompt", homebrew_update_prompt)
            homebrew_autoupdate = (
                self.homebrew_page.homebrew_autoupdate_checkbox.checkState()
                == QtCore.Qt.CheckState.Checked
            )
            self.c.gui.settings.set("homebrew_autoupdate", homebrew_autoupdate)

        self.c.gui.settings.save()
        self.finished.emit()

    def go(self):
        """
        Start the onboarding process
        """
        self.c.log("Onboarding", "go", "Starting the onboarding wizard", always=True)
        self.show()
