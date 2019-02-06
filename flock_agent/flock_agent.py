# -*- coding: utf-8 -*-
import os
import sys
import inspect
import subprocess
import requests
import tempfile
import hashlib
from colored import fg, bg, attr

class FlockAgent(object):
    def __init__(self, version):
        self.version = version
        self.print_banner()

        # Information about software to be installed
        self.software = {
            'osquery': {
                'version': '3.3.2',
                'url': 'https://pkg.osquery.io/darwin/osquery-3.3.2.pkg',
                'sha256': '6ac1baa9bd13fcf3bd4c1b20a020479d51e26a8ec81783be7a8692d2c4a9926a'
            }
        }

        # Absolute paths for binaries to subprocess
        self.bins = {
            'pkgutil': '/usr/sbin/pkgutil',
            'osascript': '/usr/bin/osascript',
            'installer': '/usr/sbin/installer'
        }

        # Path to config files within the module
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config')

    def status(self):
        """
        Check the status of all software managed by Flock Agent
        """
        all_good = True

        status = self.is_osquery_installed()
        if not status:
            all_good = False

        status = self.is_osquery_configured()
        if not status:
            all_good = False

        print('')
        if not all_good:
            print('Fix by running: {}flock-agent --install{}'.format(fg('light_blue'), attr('reset')))
            print('')

    def install(self):
        """
        Install and configure software managed by Flock Agent
        """
        tmpdir = tempfile.mkdtemp(prefix='flockagent-')

        status = self.is_osquery_installed()
        if not status:
            filename = self.download_software(tmpdir, self.software['osquery'])
            if not filename:
                self.quit_early()
                return

            self.install_pkg(filename)

            status = self.is_osquery_installed()
            if not status:
                self.print_error('osquery did not install successfully')
                self.quit_early()

        print('')

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

    def print_info(self, message):
        print('{}{}★{} {}'.format(attr('bold'), fg('light_blue'), attr('reset'), message))

    def print_error(self, message):
        print('{}{}!{} {}'.format(attr('bold'), fg('red'), attr('reset'), message))

    def quit_early(self):
        self.print_error('Encountered an error, quitting early')
        print('')

    def download_software(self, output_dir, software):
        filename = software['url'].split('/')[-1]
        download_path = os.path.join(output_dir, filename)

        # Start taking the checksum
        m = hashlib.sha256()

        # Download the software
        self.print_info('Downloading {}'.format(software['url']))
        with open(download_path, "wb") as f:
            r = requests.get(software['url'], stream=True)
            total_length = r.headers.get('content-length')

            sys.stdout.write('{}'.format(fg('light_blue')))
            if total_length is None: # no content length header
                f.write(r.content)
                m.update(r.content) # update the checksum
            else:
                dl = 0
                total_length = int(total_length)
                for data in r.iter_content(chunk_size=4096):
                    m.update(data) # update the checksum
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r%s%s" % ('▓'*done, '჻'*(50-done)))
                    sys.stdout.flush()
                sys.stdout.write('\n{}'.format(attr('reset')))
                sys.stdout.flush()

        # Check the sha256 checksum
        sha256 = m.hexdigest()
        if sha256 == software['sha256']:
            self.print_info('SHA256 checksum matches')
        else:
            self.print_error('SHA256 checksum doesn\'t match!')
            return False

        return download_path

    def install_pkg(self, filename):
        self.print_info('Type your password to install package')
        cmd = '{} -e \'do shell script "{} -pkg {} -target /" with administrator privileges\''.format(
            self.bins['osascript'], self.bins['installer'], filename)
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.print_error('Package install failed')

    def is_osquery_installed(self):
        """
        If osquery is installed, returns the version. If not installed, returns False
        """
        ret = None
        try:
            p = subprocess.run([self.bins['pkgutil'], '--pkg-info', 'com.facebook.osquery'],
                capture_output=True, check=True)
            version = p.stdout.decode().split('\n')[1].split(' ')[1]
            status = version == self.software['osquery']['version']
        except subprocess.CalledProcessError:
            # osquery isn't installed
            status = False

        self.print_status_check('osquery {} is installed'.format(self.software['osquery']['version']), status)
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

        self.print_status_check('osquery is configured properly', status)
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
