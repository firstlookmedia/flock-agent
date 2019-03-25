# Flock Agent

_**⚠️ This software is under development. It's not ready to be used in production.**_

Flock is a privacy-preserving fleet management system powered by osquery and the Elastic Stack.

The goal of Flock is to gain visibility into a fleet of laptops while protecting the privacy of the laptop users. It achieves this by only collecting information needed to inform security decisions, and by not allow the IT team to access arbitrary files, or execute arbitrary code, on the laptops they are monitoring.

![Screenshot](./assets/screenshot.png)

## Installing Flock Agent

First [install Homebrew](https://brew.sh/), if you don't already have it. Then open the Terminal app and run this:

```sh
# Add the First Look Media tap
brew tap firstlookmedia/homebrew-firstlookmedia

# Install Flock Agent
brew cask install flock-agent
```

## About Flock Agent

Flock Agent is GUI app for macOS that lives in your system tray, monitors your computer, and submits data to a Flock server. Here are some features:

- Users install Flock Agent using [Homebrew](https://brew.sh/).
- Flock Agent installs its own dependencies (like [osquery](https://osquery.io/)) using Homebrew, and also automatically keeps your Homebrew packages up-to-date.
- Flock Agent includes a number of "twigs", types of data that the agent collects and sends to the server, that focus on security-related information such as what versions of what software is installed, and what processes launch automatically. You can [see all included twigs here](./flock_agent/twigs.py).
- Before Flock Agent shares any data with the server, users must opt-in. Or, they can choose to always automatically opt-in to sending data, but the choice is with the user. Users can view exactly what data is collected for each twig before deciding to opt-in.

After launching Flock Agent for the first time, you need to register it with a Flock server, which just requires knowing the gateway URL of the server.

## Building from source

Follow the [instructions here](/BUILD.md) run Flock Agent from the source tree.
