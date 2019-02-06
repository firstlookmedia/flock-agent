# -*- coding: utf-8 -*-
import argparse
from .flock_agent import FlockAgent

flock_agent_version = 0.1


def main():
    agent = FlockAgent(flock_agent_version)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--install', action="store_true", help="Install and configure software managed by Flock Agent")
    args = parser.parse_args()

    if args.install:
        agent.exec_install()
    else:
        agent.exec_status()
