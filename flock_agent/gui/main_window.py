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

        self.update_ui()

        # Show or hide?
        if len(self.c.settings.get_undecided_twig_ids()) == 0:
            self.hide()
        else:
            self.show()

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
        twigs_tab_index = self.tabs.indexOf(self.data_tab)
        if twigs_tab_index != -1:
            self.tabs.removeTab(twigs_tab_index)
        homebrew_tab_index = self.tabs.indexOf(self.homebrew_tab)
        if homebrew_tab_index != -1:
            self.tabs.removeTab(homebrew_tab_index)

        # Add tabs that should be shown
        twigs_tab_should_show = len(self.c.settings.get_decided_twig_ids()) > 0
        if twigs_tab_should_show:
            self.tabs.insertTab(1, self.data_tab, "Data")
        opt_in_tab_should_show = len(self.c.settings.get_undecided_twig_ids()) > 0
        if opt_in_tab_should_show:
            self.tabs.insertTab(0, self.opt_in_tab, "Opt-In")
        if self.homebrew_tab.should_show:
            self.tabs.insertTab(0, self.homebrew_tab, "Homebrew")

        if active_tab == None:
            self.tabs.setCurrentIndex(0)
        else:
            if active_tab == 'opt-in':
                index = self.tabs.indexOf(self.opt_in_tab)
            elif active_tab == 'data':
                index = self.tabs.indexOf(self.data_tab)
            elif active_tab == 'homebrew':
                index = self.tabs.indexOf(self.homebrew_tab)
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

    def quit(self):
        self.c.log("MainWindow", "quit")
        self.app.quit()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
