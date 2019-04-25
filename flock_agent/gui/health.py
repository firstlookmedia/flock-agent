# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class HealthItemBase(QtWidgets.QWidget):
    def __init__(self, common, name, good_string, bad_string, query, help_url):
        super(HealthItemBase, self).__init__()
        self.c = common

        self.name = name
        self.good_string = good_string
        self.bad_string = bad_string
        self.query = query
        self.help_url = help_url

        # Widgets
        self.good_image = QtWidgets.QLabel()
        self.good_image.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/health-good.png"))))
        self.good_image.hide()
        self.bad_image = QtWidgets.QLabel()
        self.bad_image.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(self.c.get_resource_path("images/health-bad.png"))))
        self.bad_image.hide()
        self.label = QtWidgets.QLabel()
        self.help_button = QtWidgets.QPushButton('Help')
        self.help_button.setFlat(True)
        self.help_button.setStyleSheet(self.c.gui.css['link_button'])
        self.help_button.clicked.connect(self.help_button_clicked)
        self.help_button.hide()

        # Layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.good_image)
        layout.addWidget(self.bad_image)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.help_button)
        self.setLayout(layout)

        # Thread starts out as None
        self.t = None

    def refresh(self):
        self.good_image.hide()
        self.bad_image.hide()
        self.label.setText("Loading: {} ...".format(self.name))

        # Run the osquery command in a separate thread
        self.t = HealthOsqueryThread(self.c, self.name, self.query)
        self.t.query_finished.connect(self.query_finished)
        self.t.start()

    def query_finished(self, data):
        # Override this method, call either self.is_good() or self.is_bad()
        pass

    def is_good(self):
        self.good_image.show()
        self.bad_image.hide()
        self.label.setText(self.good_string)
        self.help_button.hide()

    def is_bad(self):
        self.good_image.hide()
        self.bad_image.show()
        self.label.setText(self.bad_string)
        self.help_button.show()

    def help_button_clicked(self):
        self.c.log('HealthItem', 'help_button_clicked', 'name={}, help clicked, loading {}'.format(self.name, self.help_url))
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.help_url))


class HealthOsqueryThread(QtCore.QThread):
    """
    Run the osquery command
    """
    query_finished = QtCore.pyqtSignal(list)

    def __init__(self, common, name, query):
        super(HealthOsqueryThread, self).__init__()
        self.c = common
        self.c.log('HealthOsqueryThread', '__init__', name)
        self.query = query

    def run(self):
        self.c.log('HealthOsqueryThread', 'run')
        data = self.c.osquery.exec(self.query)
        if not data:
            data = []
        self.query_finished.emit(data)


class HealthItemFileVault(HealthItemBase):
    def __init__(self, common):
        super(HealthItemFileVault, self).__init__(
            common,
            "FileVault", "FileVault is enabled", "FileVault should be enabled",
            "select disk_encryption.encrypted from mounts join disk_encryption on mounts.device_alias = disk_encryption.name where mounts.path = '/'",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-FileVault"
        )
        self.c.log('HealthItemFileVault', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # [{"encrypted":"1"}]
        self.c.log('HealthItemFileVault', 'query_finished')
        try:
            if data[0]['encrypted'] == '1':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()


class HealthItemGatekeeper(HealthItemBase):
    def __init__(self, common):
        super(HealthItemGatekeeper, self).__init__(
            common,
            "Gatekeeper", "Gatekeeper is enabled", "Gatekeeper should be enabled",
            "select assessments_enabled from gatekeeper",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-Gatekeeper"
        )
        self.c.log('HealthItemGatekeeper', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # {"assessments_enabled":"1"}
        self.c.log('HealthItemGatekeeper', 'query_finished')
        try:
            if data[0]['assessments_enabled'] == '1':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()


class HealthItemFirewall(HealthItemBase):
    def __init__(self, common):
        super(HealthItemFirewall, self).__init__(
            common,
            "Firewall", "Firewall is enabled", "Firewall should be enabled",
            "select global_state from alf",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-Firewall"
        )
        self.c.log('HealthItemFirewall', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # [{"global_state":"2"}]
        self.c.log('HealthItemFirewall', 'query_finished')
        try:
            if data[0]['assessments_enabled'] == '1' or data[0]['assessments_enabled'] == '2':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()


class HealthItemRemoteSharing(HealthItemBase):
    def __init__(self, common):
        super(HealthItemRemoteSharing, self).__init__(
            common,
            "Remote sharing", "Remote sharing is disabled", "Remote sharing should be disabled",
            "select * from sharing_preferences",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-Remote-Sharing"
        )
        self.c.log('HealthItemRemoteSharing', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # [{"bluetooth_sharing":"0","content_caching":"0","disc_sharing":"0","file_sharing":"0","internet_sharing":"0","printer_sharing":"0","remote_apple_events":"0","remote_login":"0","remote_management":"0","screen_sharing":"0"}]
        self.c.log('HealthItemRemoteSharing', 'query_finished')
        try:
            if data[0]['bluetooth_sharing'] == '0' and \
                data[0]['content_caching'] == '0' and \
                data[0]['disc_sharing'] == '0' and \
                data[0]['file_sharing'] == '0' and \
                data[0]['internet_sharing'] == '0' and \
                data[0]['printer_sharing'] == '0' and \
                data[0]['remote_apple_events'] == '0' and \
                data[0]['remote_login'] == '0' and \
                data[0]['remote_management'] == '0' and \
                data[0]['screen_sharing'] == '0':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()


class HealthItemAutoUpdates(HealthItemBase):
    def __init__(self, common):
        super(HealthItemAutoUpdates, self).__init__(
            common,
            "macOS automatic updates", "macOS automatic updates are enabled", "macOS automatic updates should be enabled",
            "select value from plist where path = '/Library/Preferences/com.apple.commerce.plist' and key = 'AutoUpdate'",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-macOS-Automatic-Updates"
        )
        self.c.log('HealthItemAutoUpdates', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # [{"value":"1"}]
        self.c.log('HealthItemAutoUpdates', 'query_finished')
        try:
            if data[0]['value'] == '1':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()


class HealthItemGuestUser(HealthItemBase):
    def __init__(self, common):
        super(HealthItemGuestUser, self).__init__(
            common,
            "Guest user", "Guest user is disabled", "Guest user should be disabled",
            "select value from plist where path='/Library/Preferences/com.apple.loginwindow.plist' and key='GuestEnabled'",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-Guest-User"
        )
        self.c.log('HealthItemGuestUser', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # [{"value":"0"}]
        self.c.log('HealthItemGuestUser', 'query_finished')
        try:
            if data[0]['value'] == '0':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()


class HealthItemSIP(HealthItemBase):
    def __init__(self, common):
        super(HealthItemSIP, self).__init__(
            common,
            "System Integrity Protection", "System Integrity Protection is enabled", "System Integrity Protection should be enabled",
            "select enabled from sip_config where config_flag='sip'",
            "https://github.com/firstlookmedia/flock-agent/wiki/Health-Check:-System-Integrity-Protection"
        )
        self.c.log('HealthItemSIP', '__init__')
        self.refresh()

    def query_finished(self, data):
        # Query response should look like:
        # [{"enabled":"1"}]
        self.c.log('HealthItemSIP', 'query_finished')
        try:
            if data[0]['enabled'] == '1':
                self.is_good()
            else:
                self.is_bad()
        except:
            self.is_bad()
