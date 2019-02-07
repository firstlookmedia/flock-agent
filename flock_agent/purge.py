# -*- coding: utf-8 -*-
import shutil
import subprocess

class Purge(object):
    """
    Functionality related to uninstalling software
    """
    def __init__(self, display):
        self.display = display

    def delete_files(self, filenames):
        """
        Delete a list of filenames
        """
        for filename in filenames:
            self.display.info('Deleting file {}'.format(filename))

        self.display.info('Type your password to delete files')
        cmd = '/usr/bin/osascript -e \'do shell script "/bin/rm -f {}" with administrator privileges\''.format(
            ' '.join(filenames))
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            self.display.error('Deleting files failed')
            return False

    def delete_dirs(self, dirs):
        """
        Delete a list of directories
        """
        for dir in dirs:
            self.display.info('Deleting directory {}'.format(dir))

        self.display.info('Type your password to delete directories')
        cmd = '/usr/bin/osascript -e \'do shell script "/bin/rm -rf {}" with administrator privileges\''.format(
            ' '.join(dirs))
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            self.display.error('Deleting directories failed')
            return False

    def run_commands(self, commands):
        """
        Run uninstall-related commands
        """
        for command in commands:
            self.display.info('Type your password to run as root: {}'.format(command))
            cmd = '/usr/bin/osascript -e \'do shell script "{}" with administrator privileges\''.format(
                command)
            try:
                subprocess.run(cmd, shell=True, capture_output=True, check=True)
            except subprocess.CalledProcessError:
                self.display.error('Command failed')
