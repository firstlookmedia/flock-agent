from PyQt5 import QtCore, QtWidgets


class SysTray(QtWidgets.QSystemTrayIcon):
    quit_signal = QtCore.pyqtSignal()

    def __init__(self, common):
        super(SysTray, self).__init__(common.gui.systray_icon)
        self.c = common

        # Show the systray icon
        self.show()
