# Build Flock Agent

Start by getting the source code:

```sh
git clone https://github.com/firstlookmedia/flock-agent.git
cd flock-agent
```

## macOS

Install Xcode from the Mac App Store. Once it's installed, run it for the first time to set it up. Also, run this to make sure command line tools are installed: `xcode-select --install`. And finally, open Xcode, go to Preferences > Locations, and make sure under Command Line Tools you select an installed version from the dropdown. (This is required for installing Qt5.)

Download and install Python 3.7.4 from https://www.python.org/downloads/release/python-374/. I downloaded `python-3.7.4-macosx10.9.pkg`.

Install Qt 5.13.0 for macOS from https://www.qt.io/offline-installers. I downloaded `qt-opensource-mac-x64-5.13.0.dmg`. In the installer, you can skip making an account, and all you need is `Qt` > `Qt 5.13.0` > `macOS`.

If you don't have it already, install pipenv (`pip3 install --user pipenv`). Then install dependencies:

```sh
pipenv install
```

Here's how you run Flock Agent, without having to build an app bundle:

```sh
pipenv run ./flock-agent -v
```

Here's how you build an app bundle:

```sh
pipenv run ./install/build_app.py
```

Now you should have `dist/Flock.app`.

Here's how you make a `.pkg` for distribution:

```sh
pipenv run install/build_pkg.py # this requires codesigning certificates
pipenv run install/build_pkg.py --without-codesign # this doesn't
```

After making a release, you should have `dist/FlockAgent-[version].pkg`.

## Linux

Install the needed dependencies:

For Fedora-like distros: `dnf install -y rpm-build python3-qt5 python3-requests python3-appdirs python3-aiohttp`

For Debian-like distros: `sudo apt install -y build-essential fakeroot python3-all python3-stdeb dh-python python3-pyqt5 python3-requests python3-appdirs python3-aiohttp`

Here's how you run Flock Agent, without having to build a package:

```sh
./flock-agent -v
```

Create a .rpm package: `./install/build_rpm.py`

Create a .deb package: `./install/build_deb.py`

# Release instructions

This section documents the release process. Unless you're a Flock Agent developer making a release, you'll probably never need to follow it.

## Changelog, version, and signed git tag

Before making a release, all of these should be complete:

- Update `flock_agent_version` in `flock-agent/__init__.py`
- There must be a PGP-signed git tag for the version, e.g. for Flock Agent 0.0.6, the tag must be `v0.0.6`
- ~~`CHANGELOG.md` should be updated to include a list of all major changes since the last release~~ (waiting until version `0.1.0` to start a changelog)

Before making a release, verify the release git tag:

```sh
git fetch
git tag -v v$VERSION
```

If the tag verifies successfully, check it out:

```
git checkout v$VERSION
```

## macOS release

To make a macOS release, go to macOS build machine:

- Build machine should be running macOS 10.13
- Verify and checkout the git tag for this release
- Run `./install/build_app.py`; this will make `dist/Flock.app` but won't codesign it
- Copy `dist/Flock.app` from the build machine to the `dist` folder on the release machine

Then move to the macOS release machine:

- Release machine should be running the latest version of macOS, and must have:
  - Apple-trusted `Developer ID Application: FIRST LOOK PRODUCTIONS, INC.` and `Developer ID Installer: FIRST LOOK PRODUCTIONS, INC.` code-signing certificates installed
  - An app-specific Apple ID password saved in the login keychain called `flockagent-notarize`
- Verify and checkout the git tag for this release
- Run `./install/build_pkg.py`; this will make a codesigned installer package called `dist/FlockAgent-$VERSION.pkg`

(These steps will eventually happen, but there's currently issues with codesigning with `--options runtime`, so saving this for later.)

- ~~Notarize it: `xcrun altool --notarize-app --primary-bundle-id "media.firstlook.flock_agent" -u "micah@firstlook.org" -p "@keychain:flockagent-notarize" --file FlockAgent-$VERSION.pkg`~~
- ~~Wait for it to get approved, check status with: `xcrun altool --notarization-history 0 -u "micah@firstlook.org" -p "@keychain:flockagent-notarize"`~~
- ~~After it's approved, staple the ticket: `xcrun stapler staple FlockAgent-$VERSION.pkg`~~

This process ends up with the final file:

```
dist/FlockAgent-$VERSION.pkg
```
