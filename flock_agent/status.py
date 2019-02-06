# -*- coding: utf-8 -*-
import os
import subprocess


class Status(object):
    """
    Functionality related to checking the status of Flock Agent
    """
    def __init__(self, display, software, config_path):
        self.display = display
        self.software = software
        self.config_path = config_path

    def is_osquery_installed(self):
        """
        Returns true if osquery is installed
        """
        ret = None
        try:
            p = subprocess.run(['/usr/sbin/pkgutil', '--pkg-info', 'com.facebook.osquery'],
                capture_output=True, check=True)
            version = p.stdout.decode().split('\n')[1].split(' ')[1]
            status = version == self.software['osquery']['version']
        except subprocess.CalledProcessError:
            # osquery isn't installed
            status = False

        self.display.status_check('osquery {} is installed'.format(self.software['osquery']['version']), status)
        return status

    def is_osquery_configured(self):
        """
        Are the osquery configuration files in the right place and contain the right content
        """
        status = True
        if not self.exists_and_has_same_content('/private/var/osquery/osquery.conf', 'osquery.conf'):
            status = False
        if not self.exists_and_has_same_content('/private/var/osquery/osquery.flags', 'osquery.flags'):
            status = False

        self.display.status_check('osquery is configured properly', status)
        return status

    def is_openjdk_installed(self):
        """
        Returns true of openjdk is installed
        """
        status = os.path.exists(self.software['openjdk']['install_path'])

        self.display.status_check('OpenJDK {} is installed'.format(self.software['openjdk']['version']), status)
        return status

    def exists_and_has_same_content(self, dest_path, src_filename):
        """
        Checks to see if the file at dest_path exists, and has the same content
        as the conf file called src_filename
        """
        expected_conf_path = os.path.join(self.config_path, src_filename)
        expected_content = open(expected_conf_path).read()

        if not os.path.exists(dest_path):
            return False
        if open(dest_path).read() != expected_content:
            return False
        return True
