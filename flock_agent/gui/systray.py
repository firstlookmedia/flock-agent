from PyQt5 import QtCore, QtWidgets


class SysTray(QtWidgets.QSystemTrayIcon):
    def __init__(self, common):
        super(SysTray, self).__init__(common.gui.systray_icon)
        self.c = common

        # Show the systray icon
        self.show()

        # Submit osquery logs to the server each minute
        self.currently_submitting = False
        self.submit_timer = QtCore.QTimer()
        self.submit_timer.timeout.connect(self.run_submit)
        self.submit_timer.start(60000) # 1 minute

    def run_submit(self):
        if self.currently_submitting:
            return
        self.currently_submitting = True

        self.t = SubmitThread(self.c)
        self.t.submit_finished.connect(self.submit_finished)
        self.t.start()

    def submit_finished(self):
        self.currently_submitting = False


class SubmitThread(QtCore.QThread):
    """
    Submit osquery records to the Flock server
    """
    submit_finished = QtCore.pyqtSignal()

    def __init__(self, common):
        super(SubmitThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('SubmitThread', 'run')
        self.c.osquery.submit_logs()
        self.submit_finished.emit()
