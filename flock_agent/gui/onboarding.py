# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class WelcomePage(QtWidgets.QWizardPage):
    def __init__(self, common):
        super(WelcomePage, self).__init__()
        self.c = common

        self.setTitle("Welcome to Flock Agent")
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/onboarding-page1.png")))
        self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, pixmap)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)


class Onboarding(QtWidgets.QWizard):
    """
    The onboarding assistant, for the first run of Flock Agent
    """
    finished = QtCore.pyqtSignal()

    def __init__(self, common):
        super(Onboarding, self).__init__()
        self.c = common
        self.c.log('Onboarding', '__init__')

        self.setWindowTitle("Configuring Flock Agent")

        self.addPage(WelcomePage(self.c))

    def done(self, result):
        super(Onboarding, self).done(result)
        self.finished.emit()

    def go(self):
        """
        Start the onboarding process
        """
        self.c.log('Onboarding', 'go', 'Starting the onboarding wizard', always=True)
        self.show()
