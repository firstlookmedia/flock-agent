#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import inspect
import subprocess
import shutil


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    build_path = os.path.join(root, 'build')
    dist_path = os.path.join(root, 'dist')
    print(build_path)
    print(dist_path)

    """ (not needed yet, not until --release works)
    # Import flock_agent to get the version
    sys.path.insert(0, root)
    import flock_agent
    version = flock_agent.flock_agent_version
    """

    print('○ Deleting old build and dist')
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    print('○ Building Flock.app')
    cmd = ['pyinstaller', 'install/pyinstaller.spec', '--clean']
    subprocess.run(cmd, cwd=root, check=True)

    print('○ Finished: dist/Flock.app')

if __name__ == '__main__':
    main()
