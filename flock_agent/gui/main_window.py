from PyQt5 import QtCore, QtWidgets, QtGui

# -*- coding: utf-8 -*-
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, common):
        super(MainWindow, self).__init__()
        self.app = app
        self.c = common

        self.c.log("MainWindow", "__init__")

        self.setWindowTitle('Flock')
        self.setWindowIcon(self.c.gui.icon)

        # Header
        header_logo_image = QtGui.QImage(self.c.get_resource_path("images/icon.png"))
        header_logo_label = QtWidgets.QLabel()
        header_logo_label.setPixmap(QtGui.QPixmap.fromImage(header_logo_image))
        header_label = QtWidgets.QLabel('<b><font color="#3461bc">Flock</font></b> monitors your computer for security issues while respecting your privacy')
        header_label.setMinimumWidth(410)
        header_label.setTextFormat(QtCore.Qt.RichText)
        header_label.setWordWrap(True)
        header_label.setStyleSheet(self.c.gui.css['header-label'])
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(header_logo_label)
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addStretch()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Limit the width to 500px
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.show()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
