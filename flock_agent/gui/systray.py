# -*- coding: utf-8 -*-
import subprocess
from PyQt5 import QtCore, QtWidgets

from .gui_common import Alert


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
        self.submit_t.submit_error.connect(self.submit_error)
        self.submit_t.start()

    def submit_finished(self):
        self.currently_submitting = False

    def submit_error(self, exception_type):
        # TODO: make the exception handling more robust
        self.showMessage("Error Submitting Data", "Exception type: {}".format(exception_type))

    def run_homebrew(self):
        self.homebrew_t = HomebrewThread(self.c)
        self.homebrew_t.homebrew_updates_available.connect(self.homebrew_updates_available)
        self.homebrew_t.homebrew_installing_updates.connect(self.homebrew_installing_updates)
        self.homebrew_t.start()

    def homebrew_updates_available(self, outdated_formulae, outdated_casks):
        self.c.log('SysTray', 'homebrew_updates_available', 'outdated_formulae: {}, outdated_casks: {}'.format(outdated_formulae, outdated_casks))

        # TODO: pass data to homebrew

        # # We can't automatically install cask upgrades, because some of them require root
        # message = """
        #     Updates are available for the following apps:<br><br><b>{}</b><br><br>
        #     Click "Install Updates" to open a Terminal and install updates using Homebrew. You may have to type your macOS password if asked.
        #     """.format("<br>".join(package_list))
        # if Alert(self.c, message, has_cancel_button=True, ok_text='Install Updates').launch():
        #     self.c.log('SysTray', 'homebrew_updates_available', 'Installing Homebrew updates in Terminal with: brew cask upgrade')
        #     subprocess.run('osascript -e \'tell application "Terminal" to do script "brew cask upgrade && exit"\'', shell=True)

    def homebrew_installing_updates(self, package_list):
        self.c.log('SysTray', 'homebrew_installing_updates', package_list)
        self.showMessage("Installing Homebrew Updates", '\n'.join(package_list))


class SubmitThread(QtCore.QThread):
    """
    Submit osquery records to the Flock server
    """
    submit_finished = QtCore.pyqtSignal()
    submit_error = QtCore.pyqtSignal(str)

    def __init__(self, common):
        super(SubmitThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('SubmitThread', 'run')
        try:
            self.c.osquery.submit_logs()
        except Exception as e:
            exception_type = type(e).__name__
            self.c.log('SubmitThread', 'run', 'Exception submitting logs: {}'.format(exception_type))
            self.submit_error.emit(exception_type)
        self.submit_finished.emit()


class HomebrewThread(QtCore.QThread):
    """
    Check for Homebrew updates
    """
    homebrew_updates_available = QtCore.pyqtSignal(list, list)
    homebrew_installing_updates = QtCore.pyqtSignal(list)

    def __init__(self, common):
        super(HomebrewThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('HomebrewThread', 'run')

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

            if homebrew_autoupdate:
                # Upgrade those formulae
                self.homebrew_installing_updates.emit(outdated_formulae)
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
            self.homebrew_updates_available.emit(outdated_formulae, outdated_casks)

    def exec(self, command):
        try:
            self.c.log('HomebrewThread', 'exec', 'Executing: {}'.format(' '.join(command)), always=True)
            p = subprocess.run(command, capture_output=True, check=True)
            return p
        except subprocess.CalledProcessError:
            self.c.log('HomebrewThread', 'exec', 'Error running command', always=True)
            return False
