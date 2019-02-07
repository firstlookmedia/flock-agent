# -*- coding: utf-8 -*-
import os
from ..item_base import ItemBase


class LogstashConfigItem(ItemBase):
    def exec_status(self):
        status = True
        if not self.is_conf_file_installed('/private/var/flock-agent/etc/logstash/logstash.conf', 'logstash.conf'):
            status = False
        if not self.is_conf_file_installed('/private/var/flock-agent/etc/logstash/co.elastic.logstash.plist', 'co.elastic.logstash.plist'):
            status = False
        if not os.path.exists('/Library/LaunchDaemons/co.elastic.logstash.plist'):
            status = False

        # Note, this isn't checking to see if the launchd is currently running because to do that
        # we need root, and I don't want to prompt for a password on status. To do that:
        # $ sudo launchctl list |grep co.elastic.logstash.plist

        self.display.status_check('logstash is configured properly', status)
        return status

    def exec_install(self):
        status = self.exec_status()
        if not status:
            if not self.copy_conf_files('/private/var/flock-agent/etc/logstash/', ['co.elastic.logstash.plist', 'logstash.conf']):
                return self.quit_early()

            if not self.install_launchd('/private/var/flock-agent/etc/logstash/co.elastic.logstash.plist'):
                return self.quit_early()

            status = self.exec_status()
            if not status:
                self.display.error('logstash could not be configured properly')
                return self.quit_early()

        return True

    def exec_purge(self):
        filenames = [
            '/Library/LaunchDaemons/co.elastic.logstash.plist'
        ]
        dirs = [
            '/private/var/flock-agent/etc/logstash/'
        ]
        commands = [
            ['/bin/launchctl', 'unload', '/Library/LaunchDaemons/co.elastic.logstash.plist']
        ]
        return (filenames, dirs, commands)
