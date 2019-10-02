#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import inspect
import subprocess
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import flock_agent

version = flock_agent.flock_agent_version
root = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))


def run(cmd):
    subprocess.run(cmd, cwd=root, check=True)


def main():
    build_path = os.path.join(root, 'build')
    dist_path = os.path.join(root, 'dist')

    print('○ Deleting old build and dist')
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    print('○ Building DEB package')
    run(['python3', 'setup.py', '--command-packages=stdeb.command', 'bdist_deb'])

    print("")
    print('○ To install run:')
    print('sudo dpkg -i deb_dist/flock-agent_{}-1_all.deb'.format(version))


if __name__ == '__main__':
    main()
