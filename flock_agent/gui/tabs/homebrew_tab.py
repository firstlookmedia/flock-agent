# -*- coding: utf-8 -*-
import subprocess
from PyQt5 import QtCore, QtWidgets, QtGui


class HomebrewTab(QtWidgets.QWidget):
    update_homebrew_tab = QtCore.pyqtSignal()

    def __init__(self, common, systray):
        super(HomebrewTab, self).__init__()
        self.c = common
        self.systray = systray

        self.c.log('HomebrewTab', '__init__')

        self.should_show = False
        self.outdated_casks = []
        self.outdated_formulae = []

        # Widgets
        self.casks_label = QtWidgets.QLabel("Updates are available for the following macOS apps:")
        self.casks_list_label = QtWidgets.QLabel()
        self.casks_list_label.setStyleSheet(self.c.gui.css['HomebrewView package_names'])
        self.formulae_label = QtWidgets.QLabel("Updates are available for the following software packages:")
        self.formulae_list_label = QtWidgets.QLabel()
        self.formulae_list_label.setStyleSheet(self.c.gui.css['HomebrewView package_names'])

        instructions_label = QtWidgets.QLabel('Click "Install Updates" to open a Terminal and install updates using Homebrew.\nYou may have to type your macOS password if asked.')

        # Buttons
        install_updates_button = QtWidgets.QPushButton("Install Updates")
        install_updates_button.clicked.connect(self.clicked_install_updates_button)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(install_updates_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.casks_label)
        layout.addWidget(self.casks_list_label)
        layout.addWidget(self.formulae_label)
        layout.addWidget(self.formulae_list_label)
        layout.addWidget(instructions_label)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        self.setLayout(layout)

        # Check for homebrew updates once every 3 hours
        self.update_check_timer = QtCore.QTimer()
        self.update_check_timer.timeout.connect(self.update_check)
        self.update_check_timer.start(10800000) # 3 hours

    def update_check(self):
        self.homebrew_thread = HomebrewUpdateCheckThread(self.c)
        self.homebrew_thread.updates_available.connect(self.updates_available)
        self.homebrew_thread.installing_updates.connect(self.installing_updates)
        self.homebrew_thread.start()

    def updates_available(self, outdated_formulae, outdated_casks):
        self.c.log('HomebrewTab', 'updates_available', 'outdated_formulae: {}, outdated_casks: {}'.format(outdated_formulae, outdated_casks))

        self.outdated_casks = outdated_casks
        self.outdated_formulae = outdated_formulae

        if len(outdated_formulae) > 0 or len(outdated_casks) > 0:
            self.should_show = True

            if len(outdated_casks) == 0:
                self.casks_label.hide()
                self.casks_list_label.hide()
            else:
                self.casks_label.show()
                self.casks_list_label.show()
                self.casks_list_label.setText('\n'.join(outdated_casks))

            if len(outdated_formulae) == 0:
                self.formulae_label.hide()
                self.formulae_list_label.hide()
            else:
                self.formulae_label.show()
                self.formulae_list_label.show()
                self.formulae_list_label.setText('\n'.join(outdated_formulae))
        else:
            self.should_show = False

        self.update_homebrew_tab.emit()

    def installing_updates(self, package_list):
        self.c.log('HomebrewTab', 'homebrew_installing_updates', package_list)
        self.systray.showMessage("Installing Homebrew Updates", '\n'.join(package_list))

    def clicked_install_updates_button(self):
        self.c.log('HomebrewTab', 'clicked_install_updates_button')

        self.should_show = False
        self.update_homebrew_tab.emit()

        cmds = []
        if len(self.outdated_formulae) > 0:
            cmds.append("brew upgrade")
        if len(self.outdated_casks) > 0:
            cmds.append("brew cask upgrade")
        cmds.append("exit")
        final_command = " && ".join(cmds)

        subprocess.run('osascript -e \'tell application "Terminal" to do script "{}"\''.format(final_command), shell=True)


class HomebrewUpdateCheckThread(QtCore.QThread):
    """
    Check for Homebrew updates
    """
    updates_available = QtCore.pyqtSignal(list, list)
    installing_updates = QtCore.pyqtSignal(list)

    def __init__(self, common):
        super(HomebrewUpdateCheckThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('HomebrewUpdateCheckThread', 'run')

        homebrew_update_prompt = self.c.settings.get('homebrew_update_prompt')
        homebrew_autoupdate = self.c.settings.get('homebrew_autoupdate')

        if homebrew_update_prompt or homebrew_autoupdate:
            # Update homebrew taps
            self.exec(['/usr/local/bin/brew', 'update'])

        outdated_formulae = []
        outdated_casks = []

        # If we want to prompt for updates, check for outdated formulae
        # Also, we need to check for these if we will autoupdate
        if homebrew_update_prompt or homebrew_autoupdate:
            # See if there are any outdated formulae
            p = self.exec(['/usr/local/bin/brew', 'outdated'])
            if p:
                stdout = p.stdout.decode().strip()
                if stdout != '':
                    outdated_formulae = [package.split(' ')[0] for package in stdout.split('\n')]

            if len(outdated_formulae) > 0 and homebrew_autoupdate:
                # Upgrade those formulae
                self.installing_updates.emit(outdated_formulae)
                self.exec(['/usr/local/bin/brew', 'upgrade'])
                outdated_formulae = []

        # If we want to prompt for updates, check for outdated casks
        if homebrew_update_prompt:
            # See if there are any outdated casks
            p = self.exec(['/usr/local/bin/brew', 'cask', 'outdated'])
            if p:
                stdout = p.stdout.decode().strip()
                if stdout != '':
                    outdated_casks = [package.split(' ')[0] for package in stdout.split('\n')]

            # Trigger the update prompt
            # Note that if autodates are enabled, outdated_formulae should be a blank list
            self.updates_available.emit(outdated_formulae, outdated_casks)

    def exec(self, command):
        try:
            self.c.log('HomebrewUpdateCheckThread', 'exec', 'Executing: {}'.format(' '.join(command)), always=True)
            p = subprocess.run(command, capture_output=True, check=True)
            return p
        except subprocess.CalledProcessError:
            self.c.log('HomebrewUpdateCheckThread', 'exec', 'Error running command', always=True)
            return False
