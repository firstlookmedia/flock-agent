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

Setup osquery config:

```sh
sudo cp -r /usr/local/Cellar/osquery/3.3.0_1/share/osquery /var/osquery
sudo cp osquery.conf /var/osquery/
```

To start `osqueryd`:

```sh
sudo osqueryctl start
```
