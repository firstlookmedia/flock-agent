#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import inspect
import subprocess
import shutil
import argparse
import requests
import hashlib


root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    )
)


def run(cmd):
    subprocess.run(cmd, cwd=root, check=True)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--without-codesign",
        action="store_true",
        dest="without_codesign",
        help="Skip codesigning",
    )
    args = parser.parse_args()

    build_path = os.path.join(root, "build")
    dist_path = os.path.join(root, "dist")
    app_path = os.path.join(dist_path, "Flock.app")

    # Make sure Flock.app already exists
    if not os.path.exists(app_path):
        print("○ App bundle doesn't exist yet, should be in: {}".format(app_path))
        return

    # Download osquery
    osquery_url = "https://pkg.osquery.io/darwin/osquery-4.0.2.pkg"
    osquery_filename = os.path.join(root, "build", "osquery-4.0.2.pkg")
    osquery_expected_sha256 = (
        "91932b1eb4a7d1ed684611f25686a5a72b7342b54ca20a990ac647ce6c42a381"
    )

    if not os.path.exists(osquery_filename):
        print("Downloading {}".format(osquery_url))
        r = requests.get(osquery_url)
        open(osquery_filename, "wb").write(r.content)
        osquery_sha256 = hashlib.sha256(r.content).hexdigest()
    else:
        osquery_data = open(osquery_filename, "rb").read()
        osquery_sha256 = hashlib.sha256(osquery_data).hexdigest()

    if osquery_sha256 != osquery_expected_sha256:
        print("ERROR! The sha256 doesn't match:")
        print("expected: {}".format(osquery_expected_sha256))
        print("  actual: {}".format(osquery_sha256))
        sys.exit(-1)

    # Import flock_agent to get the version
    sys.path.insert(0, root)
    import flock_agent

    version = flock_agent.flock_agent_version

    component_plist_path = os.path.join(root, "install/macos/packaging/component.plist")
    scripts_path = os.path.join(root, "install/macos/packaging/scripts")
    component_path = os.path.join(dist_path, "FlockAgentComponent.pkg")
    pkg_path = os.path.join(dist_path, "FlockAgent-{}.pkg".format(version))

    identity_name_application = "Developer ID Application: FIRST LOOK PRODUCTIONS, INC."
    identity_name_installer = "Developer ID Installer: FIRST LOOK PRODUCTIONS, INC."

    # Delete dist/root if it exists
    dist_path_root = os.path.join(dist_path, "root")
    if os.path.exists(dist_path_root):
        shutil.rmtree(dist_path_root)

    # Make dist/root/Applications
    os.makedirs(os.path.join(dist_path_root, "Applications"), exist_ok=True)

    # Move Flock.app there
    old_app_path = app_path
    app_path = os.path.join(dist_path_root, "Applications/Flock.app")
    shutil.move(old_app_path, app_path)

    if args.without_codesign:
        # Skip codesigning
        print("○ Creating an installer")
        run(
            [
                "pkgbuild",
                "--root",
                dist_path_root,
                "--component-plist",
                component_plist_path,
                "--scripts",
                scripts_path,
                component_path,
            ]
        )
        run(
            [
                "productbuild",
                "--package",
                component_path,
                "--package",
                osquery_filename,
                pkg_path,
            ]
        )

    else:
        # Package with codesigning
        print("○ Codesigning app bundle")
        run(["codesign", "--deep", "-s", identity_name_application, app_path])

        print("○ Creating an installer")
        run(
            [
                "pkgbuild",
                "--sign",
                identity_name_installer,
                "--root",
                dist_path_root,
                "--component-plist",
                component_plist_path,
                "--scripts",
                scripts_path,
                component_path,
            ]
        )
        run(
            [
                "productbuild",
                "--sign",
                identity_name_installer,
                "--package",
                component_path,
                "--package",
                osquery_filename,
                pkg_path,
            ]
        )

    print("○ Cleaning up")
    shutil.rmtree(dist_path_root)
    os.remove(component_path)

    print("○ Finished: {}".format(pkg_path))


if __name__ == "__main__":
    main()
