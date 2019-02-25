# -*- coding: utf-8 -*-
import os
import sys
import signal
import argparse

from .common import Common
from . import gui


flock_agent_version = 0.1


def main():
    # Allow Ctrl-C to smoothly quit the program instead of throwing an exception
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Parse arguments
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=48))
    parser.add_argument('--debug', action='store_true', dest='debug', help="Log debug output to stdout")
    #parser.add_argument('--send', action='store_true', dest='send', help="Send latest logs to server, without launching GUI")
    args = parser.parse_args()

    debug = args.debug
    #send = args.send

    # Create the common object
    common = Common(debug)

    # Launch the GUI
    gui.main(common)
