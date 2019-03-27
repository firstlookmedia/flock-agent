# -*- coding: utf-8 -*-
import os
import sys
import signal
import argparse

from .common import Common
from . import gui


flock_agent_version = '0.0.3'


def main():
    # Allow Ctrl-C to smoothly quit the program instead of throwing an exception
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Parse arguments
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=48))
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help="Display verbose output")
    parser.add_argument('--submit', action='store_true', dest='submit', help="Parse osquery logs and submit them, without opening the GUI")
    args = parser.parse_args()

    verbose = args.verbose
    submit = args.submit

    # Create the common object
    common = Common(verbose, flock_agent_version)

    if submit:
        # Submit logs
        common.osquery.submit_logs()

    else:
        # Launch the GUI
        gui.main(common)
