# -*- coding: utf-8 -*-
import os
import argparse
from .flock_agent import FlockAgent

flock_agent_version = 0.1


def main():
    agent = FlockAgent(flock_agent_version)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--install', action="store_true", help="Install and configure software managed by Flock Agent")
    group.add_argument('--purge', action="store_true", help="Completely remove software managed by Flock Agent")
    args = parser.parse_args()

    # For --install and --purge, force root
    if (args.install or args.purge) and os.geteuid() != 0:
        agent.display.root_message()
        return

    if args.install:
        return agent.exec_install()

    if args.purge:
        return agent.exec_purge()

    agent.exec_status()
