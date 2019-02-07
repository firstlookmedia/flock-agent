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

Without any commands, it will check the status of the software managed by Flock Agent.

To automatically install and configure Flock software, use `--install`:

```sh
pipenv run ./flock-agent --install
```

To uninstall all of the Flock software, use `--purge`:

```sh
pipenv run ./flock-agent --purge
```

### A note about Homebrew

At first I was going to have Flock Agent make sure Homebrew was installed, and then install osquery and logstash (and java8, which logstash requires) using `brew install`. This would be *much* simpler, but I decided against it, and here's why.

All Homebrew files are owned by the unprivileged user, so you can `brew install` stuff without `sudo`. But `osqueryd`, the background daemon, gets automatically launched as root. This means there's a privilege escalation in there. If an attacker gets a shell, they can modify `/usr/local/bin/osqueryd` (without root), and then the next time the computer reboots, when `osqueryd` gets launched as root, they've escalated privileges.

Logstash has the same problem. If `osqueryd` is run by root, then `/var/log/osquery/osqueryd.results.log` will only be readable by root, which means the logstash background daemon needs to run as root too. But if we install logstash with Homebrew it will be owned by the unprivileged user, and could facilitate the same sort of privilege escalation vulnerability.

The other option would be to run the `osqueryd` as the unprivileged user, which would remove the privilege escalation issue. However, this would make it trivial for an attacker who gets a shell to hide their tracks from osquery: they could just kill the `osqueryd` process and prevent the launch daemon from starting again.

However, I think software that Flock Agent requires, like possibly Tor, can safely be installed via Homebrew because the root user won't be running it.
