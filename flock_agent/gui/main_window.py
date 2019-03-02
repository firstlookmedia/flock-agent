# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from .tabs import OptInTab, TwigsTab, SettingsTab
from .systray import SysTray


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, common):
        super(MainWindow, self).__init__()
        self.app = app
        self.c = common

        self.c.log("MainWindow", "__init__")

        self.setWindowTitle('Flock')
        self.setWindowIcon(self.c.gui.icon)

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
        self.opt_in_tab = OptInTab(self.c)
        self.opt_in_tab.refresh.connect(self.update_ui)

        self.twigs_tab = TwigsTab(self.c)
        self.twigs_tab.refresh.connect(self.update_ui)

        self.settings_tab = SettingsTab(self.c)
        self.settings_tab.quit.connect(self.quit)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.settings_tab, "Settings")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs, stretch=1)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # System tray
        self.systray = SysTray(self.c)
        self.systray.activated.connect(self.toggle_window)

        self.update_ui()
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

        # Update the twig data in the tabs
        self.opt_in_tab.update_ui()
        self.twigs_tab.update_ui()

        # Remove tabs
        opt_in_tab_index = self.tabs.indexOf(self.opt_in_tab)
        if opt_in_tab_index != -1:
            self.tabs.removeTab(opt_in_tab_index)
        twigs_tab_index = self.tabs.indexOf(self.twigs_tab)
        if twigs_tab_index != -1:
            self.tabs.removeTab(twigs_tab_index)

        # Add tabs that should be shown
        twigs_tab_should_show = len(self.c.settings.get_decided_twig_ids()) > 0
        if twigs_tab_should_show:
            self.tabs.insertTab(0, self.twigs_tab, "Data")
        opt_in_tab_should_show = len(self.c.settings.get_undecided_twig_ids()) > 0
        if opt_in_tab_should_show:
            self.tabs.insertTab(0, self.opt_in_tab, "Opt-In")

        if active_tab == 'opt-in':
            index = self.tabs.indexOf(self.opt_in_tab)
            if index != -1:
                self.tabs.setCurrentIndex(index)
            else:
                active_tab = None
        elif active_tab == 'twigs':
            index = self.tabs.indexOf(self.twigs_tab)
            if index != -1:
                self.tabs.setCurrentIndex(index)
            else:
                active_tab = None
        if active_tab == None:
            self.tabs.setCurrentIndex(0)

    def toggle_window(self):
        self.c.log("MainWindow", "toggle_window")
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def quit(self):
        self.c.log("MainWindow", "quit")
        self.app.quit()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
