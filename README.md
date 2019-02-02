# Flock Agent

No software yet, just notes to start out with.

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

### A note about Homebrew and osquery

I've decided against installing osquery via Homebrew. By default, all Homebrew packages are owned by the unprivileged user, so you can `brew install` stuff without `sudo`. But `osqueryd`, the background daemon, gets automatically launched as root. This means there's a privilege escalation in there. If an attacker gets a shell, they can modify `/usr/local/bin/osqueryd` (without root), and then the next time the computer reboots, when `osqueryd` gets launched as root, they've escalated privileges. Instead, osquery should be installed using the [official .pkg file](https://osquery.io/downloads). Unfortunately this means there isn't an easy method to auto-update osquery. So instead, Flock Agent itself can be responsible for downloading and installing osquery updates.
