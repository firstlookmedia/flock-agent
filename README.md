# Flock Agent

No software yet, just notes to start out with.

Installing Homebrew:

```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Installing dependency packages:

```sh
# update homebrew cache
brew update
# install java8, a dependency for both osquery and logstash
brew cask install homebrew/cask-versions/java8
# install packages
brew install osquery logstash tor git
# start tor service
brew services start tor
```

Configure osquery:

```sh
sudo cp -r /usr/local/share/osquery /var/osquery
sudo cp osquery.conf /var/osquery/osquery.conf
```

Start osqueryd as background service:

```sh
sudo cp /var/osquery/com.facebook.osqueryd.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.facebook.osqueryd.plist
```

Configure logstash:

```sh
cp logstash.conf /usr/local/etc/logstash/logstash.conf
```

Start logstash as a background service:

```sh
brew services start logstash
```
