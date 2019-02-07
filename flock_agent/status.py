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
