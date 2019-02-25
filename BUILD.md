# Build instructions

Install Xcode from the Mac App Store. Once it's installed, run it for the first time to set it up. Also, run this to make sure command line tools are installed: `xcode-select --install`. And finally, open Xcode, go to Preferences > Locations, and make sure under Command Line Tools you select an installed version from the dropdown. (This is required for installing Qt5.)

Download and install Python 3.7.2 from https://www.python.org/downloads/release/python-372/. I downloaded `python-3.7.2-macosx10.9.pkg`.

Install Qt 5.11.3 from https://www.qt.io/download-open-source/. I downloaded `qt-unified-mac-x64-3.0.6-online.dmg`. In the installer, you can skip making an account, and all you need is `Qt` > `Qt 5.11.3` > `macOS`.

Now install some python dependencies with pip (note, there's issues building a .app if you install this in a virtualenv):

```sh
pip3 install -r install/requirements.txt
```

Here's how you run Flock Agent, without having to build an app bundle:

```sh
./flock-agent
```

Here's how you build an app bundle:

```sh
install/build_pkg.sh
```

Now you should have `dist/Flock.app`.

To codesign and build a .pkg for distribution:

```sh
install/build_pkg.sh --release
```

Now you should have `dist/Flock-{version}.pkg`.
