# -*- coding: utf-8 -*-
import os
import json


class Settings(object):
    def __init__(self, common):
        self.c = common
        self.settings_filename = os.path.join(self.c.appdata_path, "settings.json")
        self.c.log(
            "Settings",
            "__init__",
            "settings_filename: {}".format(self.settings_filename),
        )

        self.default_settings = {
            # First run
            "first_run": True,
            # Homebrew settings
            "homebrew_update_prompt": True,
            "homebrew_autoupdate": False,
        }

        self.load()

    def get(self, key):
        return self.settings[key]

    def set(self, key, val):
        self.c.log("Settings", "set", "{} = {}".format(key, val))
        self.settings[key] = val

    def load(self):
        self.c.log("Settings", "load")
        if os.path.isfile(self.settings_filename):
            # If the settings file exists, load it
            try:
                with open(self.settings_filename, "r") as settings_file:
                    self.settings = json.load(settings_file)

                # If it's missing any fields, add them from the default settings
                for key in self.default_settings:
                    if key not in self.settings:
                        self.settings[key] = self.default_settings[key]

            except:
                # If there's an error loading settings, fallback to default settings
                self.c.log(
                    "Settings",
                    "load",
                    "error loading settings, falling back to default",
                )
                self.settings = self.default_settings

        else:
            # Save with default settings
            self.c.log(
                "Settings", "load", "settings file doesn't exist, starting with default"
            )
            self.settings = self.default_settings

        self.save()

    def save(self):
        self.c.log("Settings", "save")
        os.makedirs(self.c.appdata_path, exist_ok=True)
        with open(self.settings_filename, "w") as settings_file:
            json.dump(self.settings, settings_file, indent=4)
