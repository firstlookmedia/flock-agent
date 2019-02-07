# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import tempfile
import shutil
import subprocess

import requests


class ItemBase(object):
    """
    An item is a piece of software or configuration that can be installed or purged
    """
    def __init__(self, display, config_path):
        self.display = display
        self.config_path = config_path

        self.tmpdir = tempfile.mkdtemp(prefix='flockagent-')

    def __exit__(self):
        shutil.rmtree(tmpdir, ignore_errors=True)

    def get_software(self):
        """
        To be overridden by child classes
        Optionally returns a dict that defines this piece of software, probably with
        at least keys 'name', 'version', 'url', and 'sha256', and possibly 'install_path'
        and 'extract_path'
        """
        return None

    def exec_status(self):
        """
        To be overridden by child classes
        Checks to see if this item is installed
        """
        pass

    def exec_install(self):
        """
        To be overridden by child classes
        Installs this item, if it's not already installed
        """
        pass

    def exec_purge(self):
        """
        To be overridden by child classes
        Returns a tuple (filenames, dirs, commands) with a list of filenames and dirs
        to delete, and commands to run, all as root, to uninstall this item
        """
        pass

    def quit_early(self):
        self.display.error('Encountered an error, quitting early')
        self.display.newline()
        return False

    def is_conf_file_installed(self, dest_path, src_filename):
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

    def download_software(self, software):
        filename = software['url'].split('/')[-1]
        download_path = os.path.join(self.tmpdir, filename)

        # Start taking the checksum
        m = hashlib.sha256()

        # Download the software
        self.display.info('Downloading {}'.format(software['url']))
        with open(download_path, "wb") as f:
            r = requests.get(software['url'], stream=True)
            total_length = r.headers.get('content-length')

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
                sys.stdout.write('\n')
                sys.stdout.flush()

        # Check the sha256 checksum
        sha256 = m.hexdigest()
        if sha256 == software['sha256']:
            self.display.info('SHA256 checksum matches')
        else:
            self.display.error('SHA256 checksum doesn\'t match!')
            return False

        return download_path

    def install_pkg(self, filename):
        self.display.info('Type your password to install package')
        cmd = '/usr/bin/osascript -e \'do shell script "/usr/sbin/installer -pkg {} -target /" with administrator privileges\''.format(
            filename)
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.display.error('Package install failed')

    def copy_conf_files(self, dest_dir, src_filenames):
        """
        Copies a list of conf files (src_filenames) into directory dest_dir, as root
        """
        for filename in src_filenames:
            self.display.info('Installing {}'.format(os.path.join(dest_dir, filename)))

        self.mkdir_if_doesnt_exist(dest_dir)

        self.display.info('Type your password to install config files')
        cmd = '/usr/bin/osascript -e \'do shell script "/bin/cp {} {}" with administrator privileges\''.format(
            ' '.join([os.path.join(self.config_path, filename) for filename in src_filenames]),
            dest_dir)
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            self.display.error('Copying files failed')
            return False

    def install_launchd(self, src_filename):
        """
        Install a launch daemon
        """
        basename = os.path.basename(src_filename)
        dest_filename = os.path.join('/Library/LaunchDaemons/', basename)

        self.display.info('Type your password to install launch daemon: {}'.format(basename))
        cmd = '/usr/bin/osascript -e \'do shell script "/bin/cp {} {}" with administrator privileges\''.format(
            src_filename, dest_filename)
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.display.error('Installing launch daemon failed')
            return False

        self.display.info('Type your password to load launch daemon: {}'.format(basename))
        cmd = '/usr/bin/osascript -e \'do shell script "/bin/launchctl load {}" with administrator privileges\''.format(
            dest_filename)
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.display.error('Installing launch daemon failed')
            return False

        return True

    def extract_tarball_as_root(self, software, src_tarball_filename):
        """
        Extract a tarball into the destination directory as root
        """
        self.mkdir_if_doesnt_exist(software['extract_path'])

        self.display.info('Type your password to install .tar.gz package to {}'.format(software['extract_path']))
        cmd = '/usr/bin/osascript -e \'do shell script "/usr/bin/tar -xf {} -C {}" with administrator privileges\''.format(
            src_tarball_filename, software['extract_path'])
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.display.error('.tar.gz package install failed')

    def mkdir_if_doesnt_exist(self, dir):
        if not os.path.exists(dir):
            self.display.info('Type your password to make directory {}'.format(dir))
            cmd = '/usr/bin/osascript -e \'do shell script "/bin/mkdir -p {}" with administrator privileges\''.format(
                dir)
            try:
                subprocess.run(cmd, shell=True, capture_output=True, check=True)
            except subprocess.CalledProcessError:
                self.display.error('Making directory failed')
