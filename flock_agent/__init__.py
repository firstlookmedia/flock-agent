# -*- coding: utf-8 -*-
import argparse
import logging
import os
import signal

from .common import Common
from . import gui
from . import daemon


flock_agent_version = "0.1.4"


def setup_logging(verbose, debug):
    logger = logging.getLogger()

    all_logger_level = logging.INFO
    console_logger_level = logging.WARNING
    basic_formatter = logging.Formatter("%(message)s")

    if debug:
        all_logger_level = logging.DEBUG
        console_logger_level = logging.DEBUG
        basic_formatter = logging.Formatter(
            "%(asctime)s: %(levelname)s - %(name)s: %(message)s"
        )
    elif verbose:
        console_logger_level = logging.INFO
        basic_formatter = logging.Formatter("%(name)s: %(levelname)s - %(message)s")

    logger.setLevel(all_logger_level)

    ch = logging.StreamHandler()
    ch.setLevel(console_logger_level)

    ch.setFormatter(basic_formatter)
    logger.addHandler(ch)


def main():
    logger = logging.getLogger("main")
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
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="Display and log debug output",
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

    setup_logging(args.verbose, args.debug)

    # Create the common object
    common = Common(verbose, flock_agent_version)

    if start_daemon:
        if os.geteuid() != 0:
            logger.error("This command must be run as root")
            return
        daemon.main(common)

    elif stop_daemon:
        if os.geteuid() != 0:
            logger.error("This command must be run as root")
            return
        daemon.stop(common)

    else:
        # Launch the GUI
        gui.main(common)
