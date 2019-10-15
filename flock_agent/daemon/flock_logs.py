import os
import time
import json

from .api_client import FlockApiClient


class FlockLog:
    def __init__(self, common, lib_dir):
        self.c = common
        self.filename = os.path.join(lib_dir, "flock.log")
        self.c.log("FlockLog", "__init__", self.filename)

        # If the log file doesn't exist, create an empty one
        if not os.path.exists(self.filename):
            open(self.filename, "a").close()
            os.chmod(self.filename, 0o600)

    def log(self, flock_log_type, twig_ids=None):
        with open(self.filename, "a") as f:
            f.write(
                json.dumps(
                    {
                        "type": flock_log_type,
                        "twig_ids": twig_ids,
                        "timestamp": int(time.time()),
                    }
                )
                + "\n"
            )
        os.chmod(self.filename, 0o600)

    def submit_logs(self):
        # Keep track of the biggest timestamp we see
        biggest_timestamp = self.c.global_settings.get("last_flock_log_timestamp")

        # What's the results file's modified timestamp, before we start the import
        try:
            mtime = os.path.getmtime(self.filename)

            # Load the log file
            with open(self.filename, "r") as f:
                lines = f.readlines()
                if len(lines) > 0:
                    self.c.log("FlockLog", "submit_logs", "{} lines".format(len(lines)))

                    # Start an API client
                    api_client = FlockApiClient(self.c)
                    try:
                        api_client.ping()
                    except:
                        self.c.log(
                            "FlockLog",
                            "submit_logs",
                            "API is not configured properly",
                            always=True,
                        )
                        return

                    # Make a list of logs
                    logs = []
                    for line in lines:
                        line = line.strip()
                        try:
                            obj = json.loads(line)
                            if "timestamp" in obj:
                                if "type" not in obj:
                                    obj["type"] = "unknown"

                                # If we haven't submitted this yet
                                if obj["timestamp"] > self.c.global_settings.get(
                                    "last_flock_log_timestamp"
                                ):
                                    logs.append(obj)
                                else:
                                    # Already submitted
                                    self.c.log(
                                        "FlockLog",
                                        "submit_logs",
                                        'skipping "{}" result, already submitted'.format(
                                            obj["type"]
                                        ),
                                    )
                            else:
                                self.c.log(
                                    "FlockLog",
                                    "submit_logs",
                                    "warning: timestamp not in line: {}".format(line),
                                )

                        except json.decoder.JSONDecodeError:
                            self.c.log(
                                "FlockLog",
                                "submit_logs",
                                "warning: line is not valid JSON: {}".format(line),
                            )

                    # Submit them
                    api_client.submit_flock_logs(json.dumps(logs))
                    self.c.log(
                        "FlockLog",
                        "submit_logs",
                        "submitted logs: {}".format(
                            ", ".join([obj["type"] for obj in logs])
                        ),
                    )

                    # Update the biggest timestamp, if needed
                    if len(logs) > 0:
                        if logs[-1]["timestamp"] > biggest_timestamp:
                            biggest_timestamp = logs[-1]["timestamp"]

            # Update timestamp in settings
            if (
                self.c.global_settings.get("last_flock_log_timestamp")
                < biggest_timestamp
            ):
                self.c.global_settings.set(
                    "last_flock_log_timestamp", biggest_timestamp
                )
                self.c.global_settings.save()

            # If the log file hasn't been modified since we started the import, truncate it
            if mtime == os.path.getmtime(self.filename):
                with open(self.filename, "w") as f:
                    f.truncate()

        except FileNotFoundError:
            self.c.log(
                "FlockLog",
                "submit_logs",
                "warning: file not found: {}".format(self.filename),
            )


class FlockLogTypes:
    SERVER_ENABLED = "server_enabled"
    SERVER_DISABLED = "server_disabled"
    TWIGS_ENABLED = "twig_enabled"
    TWIGS_DISABLED = "twig_disabled"
