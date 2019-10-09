# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

from ..twigs import twigs


class TwigView(QtWidgets.QWidget):
    """
    The view of an individual twig
    """

    def __init__(self, common, twig_id):
        super(TwigView, self).__init__()
        self.c = common
        self.twig_id = twig_id

        # Set the initial enabled status from settings
        self.enabled_status = self.get_twig()["enabled"]

        # Widgets
        self.enabled_checkbox = QtWidgets.QCheckBox(twigs[twig_id]["name"])
        if self.enabled_status == "undecided":
            self.enabled_checkbox.setTristate(True)
        else:
            self.enabled_checkbox.setTristate(False)
        self.enabled_checkbox.setStyleSheet(self.c.gui.css["TwigView enabled_checkbox"])
        self.enabled_checkbox.stateChanged.connect(self.toggle_enabled)

        description_label = QtWidgets.QLabel(twigs[twig_id]["description"])
        description_label.setWordWrap(True)

        details_button = QtWidgets.QPushButton("Details")
        details_button.setFlat(True)
        details_button.setStyleSheet(self.c.gui.css["link_button"])
        details_button.clicked.connect(self.clicked_details_button)

        # Layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.enabled_checkbox)
        top_layout.addWidget(details_button)
        top_layout.addStretch()

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(description_label, stretch=1)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 10)
        self.setLayout(layout)

        self.update_ui()

    def update_ui(self):
        if self.enabled_status == "enabled":
            self.enabled_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        elif self.enabled_status == "disabled":
            self.enabled_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            self.enabled_checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)

    def toggle_enabled(self, state):
        if state == QtCore.Qt.CheckState.Checked:
            self.enabled_status = "enabled"
            self.enabled_checkbox.setTristate(False)
        elif state == QtCore.Qt.CheckState.Unchecked:
            self.enabled_status = "disabled"
            self.enabled_checkbox.setTristate(False)
        else:
            self.enabled_status = "undecided"
            self.enabled_checkbox.setTristate(True)
        self.update_ui()

    def clicked_details_button(self):
        TwigDialog(self.c, self.twig_id)

    def get_twig(self):
        return self.c.daemon.get_twig(self.twig_id)


class TwigDialog(QtWidgets.QDialog):
    """
    A dialog box showing details about a twig
    """

    def __init__(self, common, twig_id):
        super(TwigDialog, self).__init__()
        self.c = common
        self.twig_id = twig_id

        self.c.log("TwigDialog", "__init__", twig_id)

        self.setWindowTitle("Details of: {}".format(twigs[self.twig_id]["name"]))
        self.setWindowIcon(self.c.gui.icon)
        self.setModal(True)

        self.setMinimumWidth(500)

        name_label = QtWidgets.QLabel(twigs[twig_id]["name"])
        name_label.setStyleSheet(self.c.gui.css["TwigDialog name_label"])

        interval_label = QtWidgets.QLabel(self.get_interval_string())
        interval_label.setStyleSheet(self.c.gui.css["TwigDialog interval_label"])

        description_label = QtWidgets.QLabel(twigs[twig_id]["description"])
        description_label.setWordWrap(True)
        description_label.setStyleSheet(self.c.gui.css["TwigDialog description_label"])

        osquery_label = QtWidgets.QLabel(twigs[twig_id]["query"])
        osquery_label.setStyleSheet(self.c.gui.css["TwigDialog osquery_label"])
        osquery_label.setWordWrap(True)
        osquery_layout = QtWidgets.QHBoxLayout()
        osquery_layout.addWidget(osquery_label)
        osquery_groupbox = QtWidgets.QGroupBox("Osquery SQL command")
        osquery_groupbox.setLayout(osquery_layout)

        self.table_loading_label = QtWidgets.QLabel("Loading data...")
        self.table_loading_label.show()

        self.table = QtWidgets.QTableWidget()
        table_layout = QtWidgets.QHBoxLayout()
        table_layout.addWidget(self.table)
        self.table_groupbox = QtWidgets.QGroupBox("Current data")
        self.table_groupbox.setLayout(table_layout)
        self.table_groupbox.hide()

        ok_button = QtWidgets.QPushButton("Ok")
        ok_button.clicked.connect(self.accept)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(interval_label)
        layout.addWidget(description_label)
        layout.addWidget(osquery_groupbox)
        layout.addWidget(self.table_loading_label, stretch=1)
        layout.addWidget(self.table_groupbox, stretch=1)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Run the osquery command in a separate thread
        self.t = TwigOsqueryThread(self.c, twig_id)
        self.t.query_finished.connect(self.query_finished)
        self.t.start()

        self.exec_()

    def get_interval_string(self):
        seconds = twigs[self.twig_id]["interval"]
        minutes = 0
        hours = 0
        if seconds > 60:
            minutes = seconds // 60
            seconds = seconds % 60
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60

        text = "Runs every "
        parts = []
        if hours > 0:
            parts.append("{} hours".format(hours))
        if minutes > 0:
            parts.append("{} minutes".format(minutes))
        if seconds > 0:
            parts.append("{} seconds".format(seconds))
        text += ", ".join(parts)
        return text

    def query_finished(self, data):
        self.c.log("TwigDialog", "query_finished")

        # Count rows and columns
        row_count = len(data)
        if row_count > 0:
            column_count = len(data[0])
        else:
            column_count = 0

        self.table.setRowCount(row_count)
        self.table.setColumnCount(column_count)

        # Add headers
        header_labels = []
        if row_count > 0:
            for header_label in list(data[0]):
                header_labels.append(header_label)
        self.table.setHorizontalHeaderLabels(header_labels)

        # Add data
        for row in range(row_count):
            for column, key in enumerate(list(data[row])):
                val = data[row][key]
                item = QtWidgets.QTableWidgetItem(val, QtWidgets.QTableWidgetItem.Type)
                self.table.setItem(row, column, item)

        # Hide the label and show the table
        self.table_loading_label.hide()
        self.table_groupbox.show()

        self.adjustSize()


class TwigOsqueryThread(QtCore.QThread):
    """
    Run the osquery command
    """

    query_finished = QtCore.pyqtSignal(list)

    def __init__(self, common, twig_id):
        super(TwigOsqueryThread, self).__init__()
        self.c = common
        self.twig_id = twig_id
        self.c.log("TwigOsqueryThread", "__init__", twig_id)

    def run(self):
        self.c.log("TwigOsqueryThread", "run")
        data = self.c.osquery.exec(twigs[self.twig_id]["query"])
        if not data:
            data = []
        self.query_finished.emit(data)
