# -*- coding: utf-8 -*-
import subprocess
from PyQt5 import QtCore, QtWidgets


class SysTray(QtWidgets.QSystemTrayIcon):
    def __init__(self, common):
        super(SysTray, self).__init__(common.gui.systray_icon)
        self.c = common

        # Show the systray icon
        self.show()

        # Submit osquery logs to the server each minute
        self.currently_submitting = False
        self.submit_timer = QtCore.QTimer()
        self.submit_timer.timeout.connect(self.run_submit)
        self.submit_timer.start(60000) # 1 minute

        # Check for homebrew updates once every 3 hours
        self.homebrew_timer = QtCore.QTimer()
        self.homebrew_timer.timeout.connect(self.run_homebrew)
        self.homebrew_timer.start(10800000) # 3 hours

    def run_submit(self):
        if self.currently_submitting:
            return
        self.currently_submitting = True

        self.submit_t = SubmitThread(self.c)
        self.submit_t.submit_finished.connect(self.submit_finished)
        self.submit_t.start()

    def submit_finished(self):
        self.currently_submitting = False

    def run_homebrew(self):
        self.homebrew_t = HomebrewThread(self.c)
        self.homebrew_t.homebrew_installing_updates.connect(self.homebrew_installing_updates)
        self.homebrew_t.homebrew_cask_updates_available.connect(self.homebrew_cask_updates_available)
        self.homebrew_t.start()

    def homebrew_installing_updates(self, package_list):
        self.c.log('SysTray', 'homebrew_installing_updates', package_list)
        self.showMessage("Installing Homebrew Updates", '\n'.join(package_list))

    def homebrew_cask_updates_available(self, package_list):
        self.c.log('SysTray', 'homebrew_cask_updates_available', package_list)


class SubmitThread(QtCore.QThread):
    """
    Submit osquery records to the Flock server
    """
    submit_finished = QtCore.pyqtSignal()

    def __init__(self, common):
        super(SubmitThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('SubmitThread', 'run')
        self.c.osquery.submit_logs()
        self.submit_finished.emit()


class HomebrewThread(QtCore.QThread):
    """
    Check for Homebrew updates
    """
    homebrew_installing_updates = QtCore.pyqtSignal(list)
    homebrew_cask_updates_available = QtCore.pyqtSignal(list)

    def __init__(self, common):
        super(HomebrewThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('HomebrewThread', 'run')

        autoupdate_homebrew = self.c.settings.get('autoupdate_homebrew')
        autoupdate_homebrew_cask = self.c.settings.get('autoupdate_homebrew_cask')

        if autoupdate_homebrew or autoupdate_homebrew_cask:
            # Update homebrew
            self.exec(['/usr/local/bin/brew', 'update'])

        if autoupdate_homebrew:
            # See if there are any outdated formulae
            p = self.exec(['/usr/local/bin/brew', 'outdated'])
            if p:
                stdout = p.stdout.decode().strip()
                if stdout != '':
                    package_list = [package.split(' ')[0] for package in stdout.split('\n')]
                    self.homebrew_installing_updates.emit(package_list)

                    # Upgrade those formulae
                    self.exec(['/usr/local/bin/brew', 'upgrade'])

        if autoupdate_homebrew_cask:
            # See if there are outdated casks
            p = self.exec(['/usr/local/bin/brew', 'cask', 'outdated'])
            if p:
                stdout = p.stdout.decode().strip()
                if stdout != '':
                    package_list = [package.split(' ')[0] for package in stdout.split('\n')]
                    self.homebrew_cask_updates_available.emit(package_list)

    def exec(self, command):
        try:
            self.c.log('HomebrewThread', 'exec', 'Executing: {}'.format(' '.join(command)), always=True)
            p = subprocess.run(command, capture_output=True, check=True)
            return p
        except subprocess.CalledProcessError:
            self.c.log('HomebrewThread', 'exec', 'Error running command', always=True)
            return False
