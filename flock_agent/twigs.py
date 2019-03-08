# -*- coding: utf-8 -*-

# A type of data that Flock Agent collects via osquery, and sends to a Flock
# server, is called a "twig". This file hard-codes all of the available twigs,
# and users have the option to opt-out of individual twigs.

twigs = {
    "os_version": {
        "name": "macOS version",
        "description": "The version of macOS that you're running",
        "query": "SELECT name, version, build FROM os_version;",
        "interval": 3600
    },
    "apps": {
        "name": "Installed apps",
        "description": "The names and versions of apps installed on your computer",
        "query": "SELECT name, path, bundle_identifier, bundle_short_version FROM apps;",
        "interval": 3600
    },
    "chrome_extensions": {
        "name": "Chrome extensions",
        "description": "Extensions installed in the Chrome browser",
        "query": "SELECT name, identifier, version FROM chrome_extensions;",
        "interval": 3600
    },
    "firefox_addons": {
        "name": "Firefox add-ons",
        "description": "Add-ons installed in the Firefox web browser",
        "query": "SELECT name, identifier, version, active, disabled FROM firefox_addons;",
        "interval": 3600
    },
    "browser_plugins": {
        "name": "Browser plugins",
        "description": "Browser plugins installed on your computer",
        "query": "SELECT name, identifier, version, path FROM browser_plugins;",
        "interval": 3600
    },
    "disk_encryption": {
        "name": "FileVault status",
        "description": "Whether FileVault disk encryption is enabled",
        "query": "SELECT name, encrypted, type FROM disk_encryption WHERE name='/dev/disk1s1';",
        "interval": 3600
    },
    "launchd": {
        "name": "Background services",
        "description": "What apps and services automatically run on your computer",
        "query": "SELECT path, label, keep_alive, username, program_arguments FROM launchd WHERE label NOT LIKE 'com.apple.%' AND disabled != 1;",
        "interval": 600
    },
    "heartbeat": {
        "name": "Heartbeat",
        "description": "A heartbeat counter that reports general performance (CPU, memory) and version",
        "query": "select i.*, p.resident_size, p.user_time, p.system_time, time.minutes as counter from osquery_info i, processes p, time where p.pid = i.pid;",
        "interval": 600
    }
}
