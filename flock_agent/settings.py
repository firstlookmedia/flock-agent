# -*- coding: utf-8 -*-
import os
import json


class Settings(object):
    def __init__(self, common):
        self.c = common

        self.appdata_path = os.path.expanduser("~/Library/Application Support/Flock Agent")
        self.settings_filename = os.path.join(self.appdata_path, 'settings.json')

        self.c.log("Settings", "__init__", "appdata_path: {}".format(self.appdata_path))

        self.default_settings = {
            'gateway_url': '',
            'uuid': '',
            'token': ''
        }

        self.load()

    def get(self, key):
        self.c.log("Settings", "get", key)
        return self.settings[key]

    def set(self, key, val):
        self.c.log("Settings", "set", "{} = {}".format(key, val))
        self.settings[key] = val

    def load(self):
        self.c.log("Settings", "load")
        if os.path.isfile(self.settings_filename):
            # If the settings file exists, load it
            try:
                with open(self.settings_filename, 'r') as settings_file:
                    self.settings = json.load(settings_file)
            except:
                # If there's an error loading settings, fallback to default settings
                self.c.log("Settings", "load", "error loading settings, falling back to default")
                self.settings = self.default_settings

        else:
            # Save with default settings
            self.c.log("Settings", "load", "settings file doesn't exist, starting with default")
            self.settings = self.default_settings
            self.save()

    def save(self):
        self.c.log("Settings", "save")
        os.makedirs(self.appdata_path, exist_ok=True)
        with open(self.settings_filename, 'w') as settings_file:
            json.dump(self.settings, settings_file, indent=4)
