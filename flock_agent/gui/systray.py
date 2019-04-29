# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets

from .gui_common import Alert


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

        self.submit_t = SubmitThread(self.c)
        self.submit_t.submit_finished.connect(self.submit_finished)
        self.submit_t.submit_error.connect(self.submit_error)
        self.submit_t.start()

    def submit_finished(self):
        self.currently_submitting = False

    def submit_error(self, exception_type):
        # TODO: make the exception handling more robust
        self.showMessage("Error Submitting Data", "Exception type: {}".format(exception_type))


class SubmitThread(QtCore.QThread):
    """
    Submit osquery records to the Flock server
    """
    submit_finished = QtCore.pyqtSignal()
    submit_error = QtCore.pyqtSignal(str)

    def __init__(self, common):
        super(SubmitThread, self).__init__()
        self.c = common

    def run(self):
        self.c.log('SubmitThread', 'run')
        try:
            self.c.osquery.submit_logs()
        except Exception as e:
            exception_type = type(e).__name__
            self.c.log('SubmitThread', 'run', 'Exception submitting logs: {}'.format(exception_type))
            self.submit_error.emit(exception_type)
        self.submit_finished.emit()
