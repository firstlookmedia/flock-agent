# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from .tabs import HomebrewTab, HealthTab, TwigsTab, SettingsTab

from ..common import Platform


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, common):
        super(MainWindow, self).__init__()
        self.app = app
        self.c = common

        self.c.log("MainWindow", "__init__")

        self.setWindowTitle("Flock")
        self.setWindowIcon(self.c.gui.icon)

        # System tray
        self.systray = QtWidgets.QSystemTrayIcon(self.c.gui.systray_icon)
        self.systray.activated.connect(self.toggle_window)
        self.systray.show()

        # Header
        logo = QtWidgets.QLabel()
        logo.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(self.c.get_resource_path("images/icon.png"))
            )
        )
        header_label = QtWidgets.QLabel(
            '<b><font color="#3461bc">Flock</font></b> monitors your computer for security issues while respecting your privacy'
        )
        header_label.setTextFormat(QtCore.Qt.RichText)
        header_label.setWordWrap(True)
        header_label.setStyleSheet(self.c.gui.css["MainWindow header_label"])
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addWidget(header_label, stretch=1)
        header_layout.addStretch()

        # Tabs
        if Platform.current() == Platform.MACOS:
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
        if Platform.current() == Platform.MACOS:
            self.tabs.addTab(self.health_tab, "Health")
        self.tabs.addTab(self.settings_tab, "Settings")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs, stretch=1)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.update_use_server(None)

        self.hide()

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
        if Platform.current() == Platform.MACOS:
            homebrew_tab_index = self.tabs.indexOf(self.homebrew_tab)
            if homebrew_tab_index != -1:
                self.tabs.removeTab(homebrew_tab_index)

        # Only show data or opt-in tabs if using a server
        if self.c.daemon.get("use_server"):
            data_tab_should_show = len(self.c.daemon.get_decided_twig_ids()) > 0
            if data_tab_should_show:
                # In macOS, Data tab index is 1 because Health is always 0, but in Linux it's 0
                if Platform.current() == Platform.MACOS:
                    self.tabs.insertTab(1, self.data_tab, "Data")
                else:
                    self.tabs.insertTab(0, self.data_tab, "Data")
            opt_in_tab_should_show = len(self.c.daemon.get_undecided_twig_ids()) > 0
            if opt_in_tab_should_show:
                self.tabs.insertTab(0, self.opt_in_tab, "Opt-In")

        if Platform.current() == Platform.MACOS:
            # Only show homebrew tab if there are homebrew updates available
            if self.homebrew_tab.should_show:
                self.tabs.insertTab(0, self.homebrew_tab, "Homebrew")

        # Set the active tab
        if active_tab == None:
            self.tabs.setCurrentIndex(0)
        else:
            if active_tab == "opt-in":
                index = self.tabs.indexOf(self.opt_in_tab)
            elif active_tab == "data":
                index = self.tabs.indexOf(self.data_tab)
            elif active_tab == "homebrew":
                if Platform.current() == Platform.MACOS:
                    index = self.tabs.indexOf(self.homebrew_tab)
            elif active_tab == "settings":
                index = self.tabs.indexOf(self.settings_tab)
            else:
                index = -1

            if index != -1:
                self.tabs.setCurrentIndex(index)
            else:
                self.tabs.setCurrentIndex(0)

    def update_homebrew_tab(self):
        if self.homebrew_tab.should_show:
            self.update_ui("homebrew")
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

    def update_use_server(self, active_tab="settings"):
        use_server = self.c.daemon.get("use_server")
        self.c.daemon.refresh_osqueryd()

        # Either show or hide the opt-in and data tabs
        self.update_ui(active_tab)

    def quit(self):
        self.c.log("MainWindow", "quit")
        self.app.quit()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
