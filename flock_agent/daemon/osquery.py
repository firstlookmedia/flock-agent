# -*- coding: utf-8 -*-
import json
import logging
import os
import shutil
import subprocess

from .api_client import FlockApiClient
from ..twigs import twigs
from ..common import Platform


class Osquery(object):
    """
    This class takes care of all interaction with osquery, including running queries,
    dynamically generating the config file, and making sure the daemon is running
    """

    def __init__(self, common):
        self.c = common
        logger = logging.getLogger("Osquery.__init__")
        logger.debug("")

        if Platform.current() == Platform.MACOS:
            self.osqueryi_bin = "/usr/local/bin/osqueryi"
            self.lib_dir = "/usr/local/var/lib/flock-agent"
            self.log_dir = os.path.join(self.lib_dir, "osquery_logs")
            self.config_filename = os.path.join(self.lib_dir, "osquery.conf")
            self.results_filename = os.path.join(self.log_dir, "osqueryd.results.log")
            self.plist_filename = "/Library/LaunchAgents/com.facebook.osqueryd.plist"
            os.makedirs(self.lib_dir, exist_ok=True)

            # osqueryi should be a symlink to osqueryd -- if it doesn't exist, create it
            # https://github.com/firstlookmedia/flock-agent/issues/87
            if not os.path.exists(self.osqueryi_bin):
                os.symlink("/usr/local/bin/osqueryd", self.osqueryi_bin)
            # Ensure osquery binaries have the right owners and permissions
            os.chown("/usr/local/bin/osqueryd", 0, 80)  # root:admin
            os.chmod("/usr/local/bin/osqueryd", 0o755)
            os.chown("/usr/local/bin/osqueryctl", 0, 80)  # root:admin
            os.chmod("/usr/local/bin/osqueryctl", 0o755)
        else:
            self.osqueryi_bin = "/usr/bin/osqueryi"
            self.log_dir = "/var/log/osquery"
            self.config_filename = "/etc/osquery/osquery.conf"
            self.results_filename = os.path.join(self.log_dir, "osqueryd.results.log")

        os.makedirs(self.log_dir, exist_ok=True)

        # Define the skeleton osquery config file, without any twigs
        self.config_skeleton = {
            "options": {
                "config_plugin": "filesystem",
                "logger_plugin": "filesystem",
                "logger_path": self.log_dir,
                "logger_min_status": 1,  # don't log INFO
                "schedule_splay_percent": "10",
                "utc": "true",
                "host_identifier": "uuid",
            },
            "schedule": {},
            "decorators": {
                "load": [
                    "SELECT user AS username FROM logged_in_users ORDER BY time DESC LIMIT 1;"
                ]
            },
        }

    def refresh_osqueryd(self):
        """
        Rebuild the osquery config file based on the latest settings, and restart
        the osqueryd daemon
        """
        if self.c.global_settings.get("use_server"):
            logger = logging.getLogger("Osquery.refresh_osqueryd")
            logger.info(
                f"enabling twigs: {', '.join(self.c.global_settings.get_enabled_twig_ids())}"
            )

            # Rebuild osquery config
            config = self.config_skeleton.copy()
            config["schedule"] = {}  # clear the existing schedule
            for twig_id in self.c.global_settings.get_enabled_twig_ids():
                config["schedule"][twig_id] = {
                    "query": twigs[twig_id]["query"],
                    "interval": twigs[twig_id]["interval"],
                    "description": twigs[twig_id]["description"],
                }

            # Stop osqueryd
            if Platform.current() == Platform.MACOS:
                if os.path.exists(self.plist_filename):
                    subprocess.run(["/bin/launchctl", "unload", self.plist_filename])
            elif Platform.current() == Platform.LINUX:
                subprocess.run(
                    ["/usr/bin/pkexec", "/bin/systemctl", "stop", "osqueryd"]
                )

            # Write the config file
            try:
                with open(self.config_filename, "w") as config_file:
                    json.dump(config, config_file, indent=4)
            except PermissionError:
                # TODO: hack until flock-agentd runs as root
                subprocess.run(
                    ["/usr/bin/pkexec", "/usr/bin/touch", self.config_filename]
                )
                subprocess.run(
                    [
                        "/usr/bin/pkexec",
                        "/usr/bin/chown",
                        "$USER:$USER",
                        self.config_filename,
                    ]
                )

            # Start osqueryd
            if Platform.current() == Platform.MACOS:
                shutil.copyfile(
                    self.c.get_resource_path(
                        "autostart/macos/com.facebook.osqueryd.plist"
                    ),
                    self.plist_filename,
                )
                subprocess.run(["/bin/launchctl", "load", self.plist_filename])
            elif Platform.current() == Platform.LINUX:
                subprocess.run(
                    ["/usr/bin/pkexec", "/bin/systemctl", "start", "osqueryd"]
                )
                subprocess.run(
                    ["/usr/bin/pkexec", "/bin/systemctl", "enable", "osqueryd"]
                )

        else:
            logger = logging.getLogger("Osquery.refresh_osqueryd")
            logger.info("use_server=False, so making sure osqueryd is disabled")

            if Platform.current() == Platform.MACOS:
                if os.path.exists(self.plist_filename):
                    # Stop osqueryd and delete the plist file
                    subprocess.run(["/bin/launchctl", "unload", self.plist_filename])
                    os.remove(self.plist_filename)
            elif Platform.current() == Platform.LINUX:
                subprocess.run(
                    ["/usr/bin/pkexec", "/bin/systemctl", "stop", "osqueryd"]
                )
                subprocess.run(
                    ["/usr/bin/pkexec", "/bin/systemctl", "disable", "osqueryd"]
                )

    def exec(self, query):
        """
        Run an osquery query, return the response as an object
        """
        logger = logging.getLogger("Osquery.exec")
        logger.info(query)
        try:
            p = subprocess.run(
                [self.osqueryi_bin, "--json", query], stdout=subprocess.PIPE, check=True
            )
            logger.info(f"{repr(p.stdout)}")
            return json.loads(p.stdout)
        except:
            # Error running query
            logger.info("error executing query")
            return None

    def submit_logs(self):
        """
        If there are new osquery result logs, forward them to the Flock server and
        truncate the result file.
        """
        logger = logging.getLogger("Osquery.submit_logs")
        # Keep track of the biggest timestamp we see
        biggest_timestamp = self.c.global_settings.get("last_osquery_result_timestamp")

        try:
            # What's the results file's modified timestamp, before we start the import
            mtime = os.path.getmtime(self.results_filename)

            # Load the log file
            with open(self.results_filename, "r") as results_file:
                lines = results_file.readlines()
                if len(lines) > 0:
                    logger.debug(f"{len(lines)} lines")

                    # Start an API client
                    api_client = FlockApiClient(self.c)
                    try:
                        api_client.ping()
                    except:
                        logger.warning("Unable to communicate with the server")
                        return

                    # Make a list of logs
                    logs = []
                    for line in lines:
                        line = line.strip()
                        try:
                            obj = json.loads(line)
                            if "name" not in obj:
                                obj["name"] = "unknown"

                            if "unixTime" in obj:
                                # If we haven't submitted this yet
                                if obj["unixTime"] > self.c.global_settings.get(
                                    "last_osquery_result_timestamp"
                                ):
                                    logs.append(obj)
                                else:
                                    # Already submitted
                                    logger.info(
                                        f"skipping \"{obj['name']}\" result, already submitted"
                                    )
                            else:
                                logger.warning(f"warning: unixTime not in line: {line}")

                        except json.decoder.JSONDecodeError:
                            logger.warning(f"warning: line is not valid JSON: {line}")

                    # Submit up to 200 log items at a time
                    chunks = [logs[x : x + 200] for x in range(0, len(logs), 200)]
                    for chunk in chunks:
                        api_client.submit(chunk)
                        logger.info(
                            f"submitted logs: {', '.join([obj['name'] for obj in chunk])}"
                        )

                    # Update the biggest timestamp, if needed
                    if logs[-1]["unixTime"] > biggest_timestamp:
                        biggest_timestamp = logs[-1]["unixTime"]

            # Update timestamp in settings
            if (
                self.c.global_settings.get("last_osquery_result_timestamp")
                < biggest_timestamp
            ):
                self.c.global_settings.set(
                    "last_osquery_result_timestamp", biggest_timestamp
                )
                self.c.global_settings.save()

            # If the results file hasn't been modified since we started the import, truncate it
            # (If it has been modified, this means more logs have been added, and we should wait
            # until the next this function gets called to truncate)
            if mtime == os.path.getmtime(self.results_filename):
                with open(self.results_filename, "w") as results_file:
                    results_file.truncate()

        except FileNotFoundError:
            logger.warning(f"warning: file not found: {self.results_filename}")
