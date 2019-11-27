# -*- coding: utf-8 -*-
import os
import sys
import signal
import argparse

from .common import Common
from . import gui
from . import daemon


flock_agent_version = "0.0.12"


def main():
    # Allow Ctrl-C to smoothly quit the program instead of throwing an exception
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Parse arguments
    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=48)
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Display verbose output",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        dest="start_daemon",
        help="Run the background daemon",
    )
    parser.add_argument(
        "--stop-daemon",
        action="store_true",
        dest="stop_daemon",
        help="If the background daemon is running, stop it",
    )
    args = parser.parse_args()

    verbose = args.verbose
    start_daemon = args.start_daemon
    stop_daemon = args.stop_daemon

    # Create the common object
    common = Common(verbose, flock_agent_version)

    if start_daemon:
        if os.geteuid() != 0:
            print("This command must be run as root")
            return
        daemon.main(common)

    elif stop_daemon:
        if os.geteuid() != 0:
            print("This command must be run as root")
            return
        daemon.stop(common)

    else:
        # Launch the GUI
        gui.main(common)
