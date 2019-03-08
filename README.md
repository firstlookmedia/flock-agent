# Flock Agent

Flock is a privacy-preserving fleet management system powered by osquery and the Elastic Stack.

**The goal of Flock is to gain visibility into a fleet of laptops while protecting the privacy of the laptop users. It achieves this by only collecting information needed to inform security decisions, and by not allow the IT team to access arbitrary files, or execute arbitrary code, on the laptops they are monitoring.**

See also the [Flock server](https://github.com/firstlookmedia/flock).

## About Flock Agent

Flock Agent is a GUI app that lives in your system tray, monitors your computer, and submits data to a Flock server. **It allows the user to see exactly what information they're sharing, and gives them a choice to opt-in before sharing any data.**

Flock Agent only support macOS, at the moment. It's powered by osquery. After launching Flock Agent for the first time, you need to register it with a Flock server, which just requires knowing the gateway URL of the server.

## Building from source

Follow the [instructions here](/BUILD.md) run Flock Agent from the source tree.
