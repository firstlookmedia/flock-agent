# Flock Agent

This is the macOS endpoint agent to manage the software required to send data to Flock.

## Getting started

Flock Agent isn't packaged yet. To install from the source tree, first install Python 3.7 (from python.org, or probably `brew install python@3`). Then install pipenv:

```sh
pip3 install pipenv
```

Install the pip environment:

```sh
pipenv install
```

Run the agent software like this:

```sh
pipenv run ./flock-agent
```

Without any commands, it will check the status of the software managed by Flock Agent. To actually automatically install and configure this software, use `--install`:

```sh
pipenv run ./flock-agent --install
```

## Notes

Install osquery:

```sh
wget https://pkg.osquery.io/darwin/osquery-3.3.2.pkg
shasum -a 256 osquery-3.3.2.pkg
# sha256 hash should be 6ac1baa9bd13fcf3bd4c1b20a020479d51e26a8ec81783be7a8692d2c4a9926a
sudo installer -pkg osquery-3.3.2.pkg -target /
```

Configure osquery:

```sh
sudo cp osquery.conf /private/var/osquery/osquery.conf
sudo touch /private/var/osquery/osquery.flags
```

Start osqueryd as background service:

```sh
sudo cp /private/var/osquery/com.facebook.osqueryd.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.facebook.osqueryd.plist
```

Install Homebrew:

```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install homebrew packages:

```sh
# update homebrew cache
brew update
# install java8, a dependency for logstash
brew cask install homebrew/cask-versions/java8
# install packages
brew install logstash tor git
# start tor service
brew services start tor
```

Configure logstash:

```sh
cp logstash.conf /usr/local/etc/logstash/logstash.conf
```

Start logstash as a background service:

```sh
brew services start logstash
```

### A note about Homebrew, osquery, and logstash

I've decided against installing osquery via Homebrew. By default, all Homebrew packages are owned by the unprivileged user, so you can `brew install` stuff without `sudo`. But `osqueryd`, the background daemon, gets automatically launched as root. This means there's a privilege escalation in there. If an attacker gets a shell, they can modify `/usr/local/bin/osqueryd` (without root), and then the next time the computer reboots, when `osqueryd` gets launched as root, they've escalated privileges. Instead, osquery should be installed using the [official .pkg file](https://osquery.io/downloads). Unfortunately this means there isn't an easy method to auto-update osquery. So instead, Flock Agent itself can be responsible for downloading and installing osquery updates.

After more testing, I've learned that logstash has the same problem. It needs to read `/var/log/osquery/osqueryd.results.log`, but it's only readable by root, which means the logstash background daemon needs to run as root, but if we install logstash with Homebrew it will be owned by the unprivileged user, and could facilitate a priv esc. There isn't a Mac .pkg for logstash, but there are [official binary releases](https://www.elastic.co/downloads/logstash) on the Elastic website. We can download log `logstash-6.6.0.zip`, unzip it, and then run it as root with `sudo bin/logstash -f path/to/logstash.conf`. Another issue it requires Java, so we may need to install a Java .pkg as well.

The other option would be to run the `osqueryd` as the unprivileged user, which would remove the privilege escalation issue. However, this would make it trivial for an attacker who gets code execution to hide their tracks from osquery: they could just kill the `osqueryd` process and prevent the launchd from starting again.

### Uninstalling

macOS doesn't provide a way to uninstall a .pkg, but for testing purposes you can uninstall the osquery .pkg like this:

```sh
sudo rm -r /private/var/osquery/ /usr/local/bin/osquery*
sudo pkgutil --forget com.facebook.osquery
```

Remove the osquery config like this:

```sh
sudo rm -r /private/var/osquery/osquery.conf /private/var/osquery/osquery.flags
```
