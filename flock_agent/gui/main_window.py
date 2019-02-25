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

        # Label
        label = QtWidgets.QLabel('Flock monitors your computer for security issues while respecting your privacy')

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.show()

    def shutdown(self):
        self.c.log("MainWindow", "shutdown")
