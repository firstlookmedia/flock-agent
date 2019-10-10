# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ...health import health_items
from ...common import Platform


class HealthTab(QtWidgets.QWidget):
    """
    Health
    """

    def __init__(self, common):
        super(HealthTab, self).__init__()
        self.c = common

        self.c.log("HealthTab", "__init__")

        # Health item widgets
        self.health_item_widgets = []
        for health_item in health_items[Platform.current()]:
            self.health_item_widgets.append(HealthItemWidget(self.c, health_item))

        health_item_layout = QtWidgets.QVBoxLayout()
        for widget in self.health_item_widgets:
            health_item_layout.addWidget(widget)

        # Buttons
        refresh_button = QtWidgets.QPushButton("Refresh Health Check")
        refresh_button.clicked.connect(self.refresh)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(refresh_button)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(health_item_layout)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Refresh them all
        self.refresh()

    def refresh(self):
        self.c.log("HealthTab", "refresh")
        for widget in self.health_item_widgets:
            widget.refresh()


class HealthItemWidget(QtWidgets.QWidget):
    def __init__(self, common, health_item):
        super(HealthItemWidget, self).__init__()
        self.c = common
        self.health_item = health_item

        self.c.log("HealthItemWidget", "__init__", self.health_item["name"])

        # Widgets
        self.good_image = QtWidgets.QLabel()
        self.good_image.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(self.c.get_resource_path("images/health-good.png"))
            )
        )
        self.good_image.hide()
        self.bad_image = QtWidgets.QLabel()
        self.bad_image.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(self.c.get_resource_path("images/health-bad.png"))
            )
        )
        self.bad_image.hide()
        self.label = QtWidgets.QLabel()
        self.help_button = QtWidgets.QPushButton("Help")
        self.help_button.setFlat(True)
        self.help_button.setStyleSheet(self.c.gui.css["link_button"])
        self.help_button.clicked.connect(self.help_button_clicked)
        self.help_button.hide()

        # Layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.good_image)
        layout.addWidget(self.bad_image)
        layout.addWidget(self.label)
        layout.addWidget(self.help_button)
        layout.addStretch()
        self.setLayout(layout)

        # Thread starts out as None
        self.t = None

    def refresh(self):
        self.good_image.hide()
        self.bad_image.hide()
        self.label.setText("Loading: {} ...".format(self.health_item["name"]))

        # Run the osquery command in a separate thread
        self.t = HealthOsqueryThread(self.c, self.health_item["name"])
        self.t.query_finished.connect(self.query_finished)
        self.t.start()

    def query_finished(self, data):
        if self.health_item["query_finished"](data):
            self.is_good()
        else:
            self.is_bad()

    def is_good(self):
        self.good_image.show()
        self.bad_image.hide()
        self.label.setText(self.health_item["good_string"])
        self.help_button.hide()

    def is_bad(self):
        self.good_image.hide()
        self.bad_image.show()
        self.label.setText(self.health_item["bad_string"])
        self.help_button.show()

    def help_button_clicked(self):
        self.c.log(
            "HealthItem",
            "help_button_clicked",
            "name={}, help clicked, loading {}".format(
                self.health_item["name"], self.health_item["help_url"]
            ),
        )
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.health_item["help_url"]))


class HealthOsqueryThread(QtCore.QThread):
    """
    Run the osquery command
    """

    query_finished = QtCore.pyqtSignal(list)

    def __init__(self, common, name):
        super(HealthOsqueryThread, self).__init__()
        self.c = common
        self.c.log("HealthOsqueryThread", "__init__", name)
        self.name = name

    def run(self):
        self.c.log("HealthOsqueryThread", "run")
        data = self.c.daemon.exec_health(self.name)
        if not data:
            data = []
        self.query_finished.emit(data)
