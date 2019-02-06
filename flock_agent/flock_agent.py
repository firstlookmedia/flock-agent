# -*- coding: utf-8 -*-
import os
import inspect
import subprocess
from colored import fg, bg, attr

class FlockAgent(object):
    def __init__(self, version):
        self.version = version

        # Absolute paths for binaries Flock Agent runs
        self.bins = {
            'pkgutil': '/usr/sbin/pkgutil'
        }

        # Path to config files within the module
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config')

    def print_banner(self):
        s = 'Flock Agent {}'.format(self.version)

        print('{}{}╔{}╗{}'.format( attr('bold'), fg('grey_15'), '═'*(len(s)+2), attr('reset') ))
        print('{}{}║ {}{}{} ║{}'.format( attr('bold'), fg('grey_15'), fg('yellow_3a'), s, fg('grey_15'), attr('reset') ))
        print('{}{}╚{}╝{}'.format( attr('bold'), fg('grey_15'), '═'*(len(s)+2), attr('reset') ))

    def print_status_check(self, message, passed):
        if passed:
            status = '{}{}✓{}'.format(attr('bold'), fg('green'), attr('reset'))
        else:
            status = '{}{}✘{}'.format(attr('bold'), fg('red'), attr('reset'))
        print('{} {}'.format(status, message))

    def status(self):
        """
        Check the status of all software managed by Flock Agent
        """
        self.print_banner()
        self.print_status_check('osquery 3.3.2 is installed', self.is_osquery_installed() == "3.3.2")
        self.print_status_check('osquery is configured properly', self.is_osquery_configured())
        print('')

    def is_osquery_installed(self):
        """
        If osquery is installed, returns the version. If not installed, returns False
        """
        try:
            p = subprocess.run([self.bins['pkgutil'], '--pkg-info', 'com.facebook.osquery'],
                capture_output=True, check=True)
            version = p.stdout.decode().split('\n')[1].split(' ')[1]
            return version
        except subprocess.CalledProcessError:
            # osquery isn't installed
            return False

    def is_osquery_configured(self):
        """
        Are the osquery configuration files in the right place and contain the right content
        """
        if not self.exists_and_has_same_content('/private/var/osquery/osquery.conf', 'osquery.conf'):
            return False
        if not self.exists_and_has_same_content('/private/var/osquery/osquery.flags', 'osquery.flags'):
            return False
        return True

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
