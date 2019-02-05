# -*- coding: utf-8 -*-
import subprocess
from colored import fg, bg, attr

class FlockAgent(object):
    def __init__(self, version):
        self.version = version

        self.bins = {
            'pkgutil': '/usr/sbin/pkgutil'
        }

    def print_banner(self):
        print('{}{}Flock Agent {}{}'.format( fg('white'), bg('navy_blue'), self.version, attr('reset') ))

    def print_status_check(self, message, passed):
        if len(message) > 40:
            message = message[0:40]

        if passed:
            status = '✅'
        else:
            status = '❌'

        print('{0:40s} {1:s}'.format(message, status))

        pass

    def status(self):
        self.print_banner()

        osquery_version = self.get_osquery_version()
        self.print_status_check('osquery 3.3.2 is installed', osquery_version == "3.3.2")


    def get_osquery_version(self):
        try:
            p = subprocess.run([self.bins['pkgutil'], '--pkg-info', 'com.facebook.osquery'],
                capture_output=True, check=True)
            version = p.stdout.decode().split('\n')[1].split(' ')[1]
            return version
        except subprocess.CalledProcessError:
            # osquery isn't installed
            return False
