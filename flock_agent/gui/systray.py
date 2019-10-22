from PyQt5 import QtCore, QtWidgets, QtGui

from ..common import Platform

if Platform.current() == Platform.MACOS:
    from Foundation import NSUserDefaults


class SysTray(QtWidgets.QSystemTrayIcon):
    show_clicked = QtCore.pyqtSignal()

    def __init__(self, common):
        super(SysTray, self).__init__()
        self.c = common

        menu = QtWidgets.QMenu()
        show_action = menu.addAction("Show Flock")
        show_action.triggered.connect(self.show_clicked.emit)
        self.setContextMenu(menu)

        if Platform.current() == Platform.MACOS:
            # Make sure the icon is correct every 10 seconds, in case the theme changes between light and dark
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.macos_set_correct_icon)
            self.timer.start(10000)  # 10 seconds
            self.macos_set_correct_icon()
        else:
            self.setIcon(self.c.gui.systray_icon)

    def macos_set_correct_icon(self):
        if Platform.current() == Platform.MACOS:
            if (
                NSUserDefaults.standardUserDefaults().stringForKey_(
                    "AppleInterfaceStyle"
                )
                == "Dark"
            ):
                self.setIcon(self.c.gui.systray_icon_dark)
            else:
                self.setIcon(self.c.gui.systray_icon_light)
