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
            try:
                cmd = ['/bin/rm', '-f', filename]
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                self.display.error('Deleting file {} failed'.format(filename))
                return False

        return True

    def delete_dirs(self, dirs):
        """
        Delete a list of directories
        """
        for dir in dirs:
            self.display.info('Deleting directory {}'.format(dir))
            try:
                cmd = ['/bin/rm', '-rf', dir]
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                self.display.error('Deleting directory {} failed'.format(dir))
                return False

        return True

    def run_commands(self, commands):
        """
        Run uninstall-related commands
        """
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                self.display.error('Command failed: {}'.format(' '.join(cmd)))
