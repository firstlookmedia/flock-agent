# -*- coding: utf-8 -*-
import os
import json

from ..twigs import twigs
from ..common import Platform


class GlobalSettings(object):
    def __init__(self, common):
        self.c = common

        if Platform.current() == Platform.MACOS:
            etc_dir = "/usr/local/etc/flock-agent"
        else:
            etc_dir = "/etc/flock-agent"
        os.makedirs(etc_dir, exist_ok=True)
        self.settings_filename = os.path.join(etc_dir, "global_settings.json")

        self.c.log(
            "GlobalSettings",
            "__init__",
            "settings_filename: {}".format(self.settings_filename),
        )

        self.default_settings = {
            # Server settings
            "use_server": True,
            "gateway_url": None,
            "gateway_token": None,
            "gateway_username": None,
            "automatically_enable_twigs": False,
            "last_osquery_result_timestamp": 0,  # Timestamp of the last osquery result sent to the server
            # Twigs
            "twigs": {},
        }

        # Note that settings.twigs is a dictionary that maps twig_ids to dicts that describe
        # the twig. Those dicts include the fields 'query' and 'enabled', where 'enabled'
        # is either 'undecided', 'enabled', or 'disabled'.

        self.load()

    def get(self, key):
        return self.settings[key]

    def set(self, key, val):
        self.c.log("GlobalSettings", "set", "{} = {}".format(key, val))
        self.settings[key] = val

    def get_twig(self, twig_id):
        return self.settings["twigs"][twig_id]

    def enable_twig(self, twig_id):
        self.settings["twigs"][twig_id]["enabled"] = "enabled"

    def disable_twig(self, twig_id):
        self.settings["twigs"][twig_id]["enabled"] = "disabled"

    def get_decided_twig_ids(self):
        twig_ids = []
        for twig_id in self.settings["twigs"]:
            if self.settings["twigs"][twig_id]["enabled"] != "undecided":
                twig_ids.append(twig_id)
        return twig_ids

    def get_undecided_twig_ids(self):
        twig_ids = []
        for twig_id in self.settings["twigs"]:
            if self.settings["twigs"][twig_id]["enabled"] == "undecided":
                twig_ids.append(twig_id)
        return twig_ids

    def get_enabled_twig_ids(self):
        twig_ids = []
        for twig_id in self.settings["twigs"]:
            if self.settings["twigs"][twig_id]["enabled"] == "enabled":
                twig_ids.append(twig_id)
        return twig_ids

    def load(self):
        self.c.log("GlobalSettings", "load")
        if os.path.isfile(self.settings_filename):
            self.first_run = False

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
                    "GlobalSettings",
                    "load",
                    "error loading settings, falling back to default",
                )
                self.settings = self.default_settings

        else:
            self.first_run = True

            # Save with default settings
            self.c.log(
                "GlobalSettings",
                "load",
                "settings file doesn't exist, starting with default",
            )
            self.settings = self.default_settings

            # Figure out the default gateway username
            res = self.c.osquery.exec("SELECT uuid AS host_uuid FROM system_info;")
            if res:
                self.set("gateway_username", res[0]["host_uuid"])

        # Fill in new twigs, and update existing twigs
        for twig_id in twigs:
            if Platform.current() in twigs[twig_id]["platforms"]:
                add = False
                if twig_id in self.settings["twigs"]:
                    if (
                        self.settings["twigs"][twig_id]["query"]
                        != twigs[twig_id]["query"]
                    ):
                        # The query has changed, so change enabled to undecided
                        add = True

                else:
                    # The twig doesn't exist, so add it
                    add = True

                # Add or update the twig
                if add:
                    if self.settings["automatically_enable_twigs"]:
                        enabled_state = "enabled"
                    else:
                        enabled_state = "undecided"

                    self.settings["twigs"][twig_id] = {
                        "query": twigs[twig_id]["query"],
                        "enabled": enabled_state,
                    }
            else:
                if twig_id in self.settings["twigs"]:
                    del self.settings["twigs"][twig_id]

        # Delete obsolete twigs
        twig_ids = [twig_id for twig_id in self.settings["twigs"]]
        for twig_id in twig_ids:
            if twig_id not in twigs:
                del self.settings["twigs"][twig_id]

        self.save()

    def save(self):
        self.c.log("GlobalSettings", "save")
        os.makedirs(self.c.appdata_path, exist_ok=True)
        with open(self.settings_filename, "w") as settings_file:
            json.dump(self.settings, settings_file, indent=4)
        os.chmod(self.settings_filename, 0o600)