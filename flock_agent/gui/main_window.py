# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from .tabs import HomebrewTab, HealthTab, TwigsTab, SettingsTab
from .systray import SysTray


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, common):
        super(MainWindow, self).__init__()
        self.app = app
        self.c = common

        self.c.log("MainWindow", "__init__")

        self.setWindowTitle('Flock')
        self.setWindowIcon(self.c.gui.icon)

        # System tray
        self.systray = SysTray(self.c)
        self.systray.activated.connect(self.toggle_window)

        # Header
        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/icon.png"))))
        header_label = QtWidgets.QLabel('<b><font color="#3461bc">Flock</font></b> monitors your computer for security issues while respecting your privacy')
        header_label.setTextFormat(QtCore.Qt.RichText)
        header_label.setWordWrap(True)
        header_label.setStyleSheet(self.c.gui.css['MainWindow header_label'])
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addWidget(header_label, stretch=1)
        header_layout.addStretch()

        # Tabs
        self.homebrew_tab = HomebrewTab(self.c, self.systray)
        self.homebrew_tab.update_homebrew_tab.connect(self.update_homebrew_tab)

        self.health_tab = HealthTab(self.c)

        self.opt_in_tab = TwigsTab(self.c, is_opt_in=True)
        self.opt_in_tab.refresh.connect(self.update_ui)

        self.data_tab = TwigsTab(self.c, is_opt_in=False)
        self.data_tab.refresh.connect(self.update_ui)

        self.settings_tab = SettingsTab(self.c)
        self.settings_tab.update_use_server.connect(self.update_use_server)
        self.settings_tab.quit.connect(self.quit)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.health_tab, "Health")
        self.tabs.addTab(self.settings_tab, "Settings")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs, stretch=1)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Show or hide?
        if len(self.c.settings.get_undecided_twig_ids()) == 0:
            self.hide()
        else:
            self.show()

        # Submit osquery logs to the server on a timer
        self.currently_submitting = False
        self.submit_timer = QtCore.QTimer()
        self.submit_timer.timeout.connect(self.run_submit)
        self.update_use_server(None) # this calls self.update_ui()

    def closeEvent(self, e):
        """
        Intercept close event, and instead minimize to systray
        """
        self.c.log("MainWindow", "closeEvent", "Hiding window")
        self.hide()
        e.ignore()

    def update_ui(self, active_tab=None):
        self.c.log("MainWindow", "update_ui")

        # Update the tabs
        self.opt_in_tab.update_ui()
        self.data_tab.update_ui()
        self.settings_tab.update_ui()

        # Remove tabs
        opt_in_tab_index = self.tabs.indexOf(self.opt_in_tab)
        if opt_in_tab_index != -1:
            self.tabs.removeTab(opt_in_tab_index)
        data_tab_index = self.tabs.indexOf(self.data_tab)
        if data_tab_index != -1:
            self.tabs.removeTab(data_tab_index)
        homebrew_tab_index = self.tabs.indexOf(self.homebrew_tab)
        if homebrew_tab_index != -1:
            self.tabs.removeTab(homebrew_tab_index)

        # Only show data or opt-in tabs if using a server
        if self.c.settings.get('use_server'):
            data_tab_should_show = len(self.c.settings.get_decided_twig_ids()) > 0
            if data_tab_should_show:
                self.tabs.insertTab(1, self.data_tab, "Data")
            opt_in_tab_should_show = len(self.c.settings.get_undecided_twig_ids()) > 0
            if opt_in_tab_should_show:
                self.tabs.insertTab(0, self.opt_in_tab, "Opt-In")

        # Only show homebrew tab if there are homebrew updates available
        if self.homebrew_tab.should_show:
            self.tabs.insertTab(0, self.homebrew_tab, "Homebrew")

        # Set the active tab
        if active_tab == None:
            self.tabs.setCurrentIndex(0)
        else:
            if active_tab == 'opt-in':
                index = self.tabs.indexOf(self.opt_in_tab)
            elif active_tab == 'data':
                index = self.tabs.indexOf(self.data_tab)
            elif active_tab == 'homebrew':
                index = self.tabs.indexOf(self.homebrew_tab)
            elif active_tab == 'settings':
                index = self.tabs.indexOf(self.settings_tab)
            else:
                index = -1

            if index != -1:
                self.tabs.setCurrentIndex(index)
            else:
                self.tabs.setCurrentIndex(0)

    def update_homebrew_tab(self):
        if self.homebrew_tab.should_show:
            self.update_ui('homebrew')
            if not self.isVisible():
                self.show()
                self.activateWindow()
                self.raise_()
        else:
            self.update_ui()

    def toggle_window(self):
        self.c.log("MainWindow", "toggle_window")
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.raise_()

    def run_submit(self):
        if self.currently_submitting:
            return
        self.currently_submitting = True

        self.submit_thread = SubmitThread(self.c)
        self.submit_thread.submit_finished.connect(self.submit_finished)
        self.submit_thread.submit_error.connect(self.submit_error)
        self.submit_thread.start()

    def submit_finished(self):
        self.currently_submitting = False

    def submit_error(self, exception_type):
        # TODO: make the exception handling more robust
        self.systray.showMessage("Error Submitting Data", "Exception type: {}".format(exception_type))

    def update_use_server(self, active_tab='settings'):
        use_server = self.c.settings.get('use_server')

        if use_server:
            # Start the submit timer
            self.submit_timer.start(60000) # 1 minute

        else:
            # Stop the submit timer
            self.submit_timer.stop()

        self.update_ui(active_tab)

    def quit(self):
        self.c.log("MainWindow", "quit")
        self.app.quit()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")


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
        if self.c.settings.get('use_server'):
            self.c.log('SubmitThread', 'run')

            try:
                self.c.osquery.submit_logs()
            except Exception as e:
                exception_type = type(e).__name__
                self.c.log('SubmitThread', 'run', 'Exception submitting logs: {}'.format(exception_type))
                self.submit_error.emit(exception_type)

        else:
            self.c.log('SubmitThread', 'run', 'use_server=False, so skipping')

        self.submit_finished.emit()
