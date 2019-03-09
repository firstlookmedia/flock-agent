#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import inspect
import subprocess
import shutil


root = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))


def run(cmd):
    subprocess.run(cmd, cwd=root, check=True)


def main():
    is_release = '--release' in sys.argv

    build_path = os.path.join(root, 'build')
    dist_path = os.path.join(root, 'dist')
    app_path = os.path.join(dist_path, 'Flock.app')

    print('○ Deleting old build and dist')
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    print('○ Building app bundle')
    run(['pyinstaller', 'install/pyinstaller.spec', '--clean'])
    shutil.rmtree(os.path.join(dist_path, 'flock-agent'))

    if not is_release:
        print('○ Finished: {}'.format(app_path))

    else:
        # Import flock_agent to get the version
        sys.path.insert(0, root)
        import flock_agent
        version = flock_agent.flock_agent_version

        component_plist_path = os.path.join(root, 'install/macos-packaging/component.plist')
        scripts_path = os.path.join(root, 'install/macos-packaging/scripts')
        component_path = os.path.join(dist_path, 'FlockAgentComponent.pkg')
        product_path = os.path.join(dist_path, 'FlockAgent-{}.pkg'.format(version))

        identity_name_application = "Developer ID Application: FIRST LOOK PRODUCTIONS, INC."
        identity_name_installer = "Developer ID Installer: FIRST LOOK PRODUCTIONS, INC."

        print('○ Codesigning app bundle')
        run(['codesign', '--deep', '-s', identity_name_application, app_path])

        print('○ Creating an installer')
        run(['pkgbuild', '--sign', identity_name_installer, '--root', dist_path, '--component-plist', component_plist_path, '--scripts', scripts_path, component_path])
        run(['productbuild', '--sign', identity_name_installer, '--package', component_path, product_path])

        print('○ Cleaning up')
        shutil.rmtree(app_path)
        os.remove(component_path)

        print('○ Finished: {}'.format(product_path))

if __name__ == '__main__':
    main()
