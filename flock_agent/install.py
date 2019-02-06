# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import tempfile
import shutil
import subprocess

import requests


class Install(object):
    """
    Functionality related to installing software
    """
    def __init__(self, display, status, software, config_path):
        self.display = display
        self.status = status
        self.software = software
        self.config_path = config_path

        self.tmpdir = tempfile.mkdtemp(prefix='flockagent-')

    def __exit__(self):
        shutil.rmtree(tmpdir, ignore_errors=True)

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

    def copy_files_as_root(self, dest_dir, src_filenames):
        """
        Copies a list of conf files (src_filenames) into directory dest_dir, as root
        """
        for filename in src_filenames:
            self.display.info('Installing {}'.format(os.path.join(dest_dir, filename)))

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

    def extract_tarball_as_root(self, software, src_tarball_filename):
        """
        Extract a tarball into the destination directory as root
        """
        self.display.info('Type your password to install .tar.gz package')
        cmd = '/usr/bin/osascript -e \'do shell script "/usr/bin/tar -xf {} -C {}" with administrator privileges\''.format(
            src_tarball_filename, software['extract_path'])
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.display.error('.tar.gz package install failed')
