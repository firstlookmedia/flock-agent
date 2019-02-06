# -*- coding: utf-8 -*-
import os
import inspect
import subprocess
from colored import fg, bg, attr

class FlockAgent(object):
    def __init__(self, version):
        self.version = version
        self.print_banner()

        # Information about software to be installed
        self.software = {
            'osquery': {
                'version': '3.3.2',
                'download_url': 'https://pkg.osquery.io/darwin/osquery-3.3.2.pkg',
                'sha256': '6ac1baa9bd13fcf3bd4c1b20a020479d51e26a8ec81783be7a8692d2c4a9926a'
            }
        }

        # Absolute paths for binaries to subprocess
        self.bins = {
            'pkgutil': '/usr/sbin/pkgutil'
        }

        # Path to config files within the module
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config')

    def print_banner(self):
        s = 'Flock Agent {}'.format(self.version)

        print('{}{}╔{}╗{}'.format( attr('bold'), fg('dark_green_sea'), '═'*(len(s)+2), attr('reset') ))
        print('{}{}║ {}{}{} ║{}'.format( attr('bold'), fg('light_sky_blue_3a'), fg('light_yellow'), s, fg('light_sky_blue_3a'), attr('reset') ))
        print('{}{}╚{}╝{}'.format( attr('bold'), fg('light_sky_blue_3b'), '═'*(len(s)+2), attr('reset') ))

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
        all_good = True

        status = self.is_osquery_installed() == self.software['osquery']['version']
        if not status:
            all_good = False
        self.print_status_check('osquery {} is installed'.format(self.software['osquery']['version']), status)

        status = self.is_osquery_configured()
        if not status:
            all_good = False
        self.print_status_check('osquery is configured properly', self.is_osquery_configured())
        print('')

        if not all_good:
            print('Fix by running: {}flock-agent --install{}'.format(fg('light_blue'), attr('reset')))
            print('')

    def install(self):
        """
        Install and configure software managed by Flock Agent
        """
        pass

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
