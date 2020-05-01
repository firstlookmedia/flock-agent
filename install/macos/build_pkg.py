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


def runtime_harden_osquery(build_path, osquery_filename, identity_name_application):
    print(
        "○ Extracting osquery package, re-signing it with hardened runtime, and flatting it"
    )
    hardened_osquery_filename = os.path.splitext(osquery_filename)[0] + "-hardened.pkg"

    osquery_expanded_path = os.path.join(build_path, "osquery")
    os.makedirs(osquery_expanded_path, exist_ok=True)

    # Expand the osquery package
    run(
        [
            "pkgutil",
            "--expand",
            osquery_filename,
            os.path.join(osquery_expanded_path, "Contents"),
        ]
    )

    # Rename Payload to Payload.cpio.gz, and extract it
    shutil.move(
        os.path.join(osquery_expanded_path, "Contents/Payload"),
        os.path.join(osquery_expanded_path, "Contents/Payload.cpio.gz"),
    )
    os.makedirs(os.path.join(osquery_expanded_path, "Contents/Payload"), exist_ok=True)
    subprocess.run(
        "gzip -dc ../Payload.cpio.gz | cpio -idm -",
        shell=True,
        cwd=os.path.join(osquery_expanded_path, "Contents/Payload"),
    )

    # Re-sign osqueryd, with hardened runtime enabled
    run(
        [
            "codesign",
            "--remove-signature",
            os.path.join(
                osquery_expanded_path, "Contents/Payload/usr/local/bin/osqueryd"
            ),
        ]
    )
    run(
        [
            "codesign",
            "-s",
            identity_name_application,
            "-o",
            "runtime",
            os.path.join(
                osquery_expanded_path, "Contents/Payload/usr/local/bin/osqueryd"
            ),
        ]
    )

    # Recompress the payload
    os.remove(os.path.join(osquery_expanded_path, "Contents/Payload.cpio.gz"))
    subprocess.run(
        "find . -print -depth | cpio -ov > ../Payload.cpio",
        shell=True,
        cwd=os.path.join(osquery_expanded_path, "Contents/Payload"),
    )
    run(["gzip", os.path.join(osquery_expanded_path, "Contents/Payload.cpio")])
    shutil.rmtree(os.path.join(osquery_expanded_path, "Contents/Payload"))
    shutil.move(
        os.path.join(osquery_expanded_path, "Contents/Payload.cpio.gz"),
        os.path.join(osquery_expanded_path, "Contents/Payload"),
    )

    # Flatten the osquery package
    run(
        [
            "pkgutil",
            "--flatten",
            os.path.join(osquery_expanded_path, "Contents"),
            hardened_osquery_filename,
        ]
    )
    return hardened_osquery_filename


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
    osquery_url = "https://pkg.osquery.io/darwin/osquery-4.3.0.pkg"
    osquery_filename = os.path.join(root, "build", "osquery-4.3.0.pkg")
    osquery_expected_sha256 = (
        "197eae9624ec830bf3fec53b79b11e084792a04a461c3241d95cf6aebd3e6ac2"
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
    entitlements_plist_path = os.path.join(
        root, "install/macos/packaging/entitlements.plist"
    )
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
        # Re-sign osquery binary, with hardened runtime enabled
        hardened_osquery_filename = runtime_harden_osquery(
            build_path, osquery_filename, identity_name_application
        )

        # Package with codesigning
        print("○ Codesigning app bundle")
        run(
            [
                "codesign",
                "--deep",
                "-s",
                identity_name_application,
                "--entitlements",
                entitlements_plist_path,
                "-o",
                "runtime",
                app_path,
            ]
        )

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
                hardened_osquery_filename,
                pkg_path,
            ]
        )

    print("○ Cleaning up")
    shutil.rmtree(dist_path_root)
    os.remove(component_path)

    print("○ Finished: {}".format(pkg_path))


if __name__ == "__main__":
    main()
