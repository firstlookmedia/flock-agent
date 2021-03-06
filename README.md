# Flock Agent

Flock is the privacy-preserving fleet management system. The goal of Flock is to gain visibility into a fleet of workstation computers while protecting the privacy of their users. It achieves this by only collecting information needed to inform security decisions, and by not allowing the IT team to access arbitrary files or execute arbitrary code on the computers they are monitoring.

Flock Agent is available for macOS and Linux. It runs on endpoints, collects data, and shares it with the [Flock server](https://github.com/firstlookmedia/flock-server).

## Installing

To install Flock Agent, follow [these instructions](https://github.com/firstlookmedia/flock-agent/wiki/Installing-Flock-Agent).

## Why use Flock Agent?

### Health check

The agent lets users quickly check on the security best practices of their Mac. If any best practice isn't being followed, the user can click "Help" to load a wiki page with instructions for hardening their system.

![Health screenshot](./assets/screenshot1.png)

### Homebrew Updates

The agent prompts users when software installed via Homebrew (both formulae and casks) is out-of-date, helping keep all of their software patched.

![Homebrew screenshot](./assets/screenshot4.png)

### Data collection

Flock Agent is useful for both individuals and organizations. If you're deploying Flock as part of your organization, the agent will collects specific pieces of data that are helpful for you to assess your organization's security posture and detect attacks. Users can choose not to opt-in to any of these types of data if they wish.

![Data screenshot](./assets/screenshot2.png)

Users can click "Details" next to any type of data to see exactly what data is collected from their computer, how frequently, and what the osquery SQL query being run is.

![Data screenshot](./assets/screenshot3.png)

## How it works

Flock Agent is GUI app for macOS that lives in your system tray, monitors your computer, and submits data to a Flock server. Here are some features:

- Users install Flock Agent using [Homebrew](https://brew.sh/).
- Flock Agent installs its own dependencies (like [osquery](https://osquery.io/)) using Homebrew, and also automatically keeps your Homebrew packages up-to-date.
- Flock Agent has a "health check", allowing users to assess the security health of their computer, and help them start using best practices.
- Flock Agent includes "twigs", osquery SQL queries that get run at regular intervals and send the results to the server. (You know, because birds collect twigs and bring them back to their server.) The twigs focus on security-related information, such as what versions of what software is installed, and what processes launch automatically. You can [see all included twigs here](./flock_agent/twigs.py).
- Before Flock Agent shares any data with the server, users must opt-in. Or, they can choose to always automatically opt-in to sending data, but the choice is with the user. Users can view exactly what data is collected for each twig before deciding to opt-in.

After launching Flock Agent for the first time, you need to register it with a Flock server, which just requires knowing the gateway URL of the server.

## Advanced usage

If you'd like to see what Flock Agent is doing as it's doing it, you can open it in verbose mode. First, click the Flock icon in the system tray, switch to the Settings tab, and click "Quit Flock Agent". Then open the Terminal app and run:

```sh
/Applications/Flock.app/Contents/MacOS/flock-agent -v
```

This will output verbose information in the Terminal about what Flock Agent is doing.

## Building from source

Follow the [instructions here](./BUILD.md) run Flock Agent from the source tree.

## Completely uninstalling Flock Agent in macOS

If you installed Flock Agent using Homebrew in macOS, you can completely uninstall it with `brew cask uninstall flock-agent`.

Otherwise, run these commands to delete everything:

```
# Remove osquery
sudo launchctl unload /Library/LaunchDaemons/com.facebook.osqueryd.plist
sudo rm /Library/LaunchDaemons/com.facebook.osqueryd.plist
sudo rm -rf /private/var/log/osquery
sudo rm -rf /private/var/osquery
sudo rm /usr/local/bin/osquery*
sudo pkgutil --forget com.facebook.osquery

# Remove Flock Agent
sudo launchctl unload /Library/LaunchDaemons/media.firstlook.flock-agentd.plist
sudo rm /Library/LaunchDaemons/media.firstlook.flock-agentd.plist
sudo rm -rf /Applications/Flock.app
sudo rm -rf /usr/local/etc/flock-agent
sudo rm -rf /usr/local/var/lib/flock-agent
sudo rm -rf /usr/local/var/log/flock-agent
sudo pkgutil --forget media.firstlook.flock-agent
rm -r ~/Library/Application\ Support/FlockAgent/
```

## License

Flock Agent is released under [GPLv3](./LICENSE.md).

Other licenses:

* [requests-unixsocket](https://github.com/msabramo/requests-unixsocket/), Apache License 2.0 (code is bundled in this project instead of as a dependency because it's not packaged in Fedora)
