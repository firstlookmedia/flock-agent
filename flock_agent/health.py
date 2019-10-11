# -*- coding: utf-8 -*-

# The health tab includes osquery SQL commands that can be run to check up on the health
# of the computer that the agent is running in. This is a hard-coded list of health items,
# to avoid allowing the daemon to execute arbitrary osquery SQL commands from unprivileged
# users.


def macos_filevault_query_finished(data):
    # Query response should look like:
    # [{"encrypted":"1"}]
    try:
        if data[0]["encrypted"] == "1":
            return True
        else:
            return False
    except:
        return False


def macos_gatekeeper_query_finished(data):
    # Query response should look like:
    # {"assessments_enabled":"1"}
    try:
        if data[0]["assessments_enabled"] == "1":
            return True
        else:
            return False
    except:
        return False


def macos_firewall_query_finished(data):
    # Query response should look like:
    # [{"global_state":"2"}]
    try:
        if data[0]["global_state"] == "1" or data[0]["global_state"] == "2":
            return True
        else:
            return False
    except:
        return False


def macos_remote_sharing_query_finished(data):
    # Query response should look like:
    # [{"bluetooth_sharing":"0","content_caching":"0","disc_sharing":"0","file_sharing":"0","internet_sharing":"0","printer_sharing":"0","remote_apple_events":"0","remote_login":"0","remote_management":"0","screen_sharing":"0"}]
    try:
        if (
            data[0]["bluetooth_sharing"] == "0"
            and data[0]["content_caching"] == "0"
            and data[0]["disc_sharing"] == "0"
            and data[0]["file_sharing"] == "0"
            and data[0]["internet_sharing"] == "0"
            and data[0]["printer_sharing"] == "0"
            and data[0]["remote_apple_events"] == "0"
            and data[0]["remote_login"] == "0"
            and data[0]["remote_management"] == "0"
            and data[0]["screen_sharing"] == "0"
        ):
            return True
        else:
            return False
    except:
        return False


def macos_automatic_updates_query_finished(data):
    # Query response should look like:
    # [{"value":"1"}]
    try:
        if data[0]["value"] == "1":
            return True
        else:
            return False
    except:
        return False


def macos_guest_user_query_finished(data):
    # Query response should look like:
    # [{"value":"0"}]
    try:
        if data[0]["value"] == "0":
            return True
        else:
            return False
    except:
        return False


def macos_sip_query_finished(data):
    # Query response should look like:
    # [{"enabled":"1"}]
    try:
        if data[0]["enabled"] == "1":
            return True
        else:
            return False
    except:
        return False


health_items = {
    "macos": [
        {
            "name": "FileVault",
            "good_string": "FileVault is enabled",
            "bad_string": "FileVault should be enabled",
            "query": "select disk_encryption.encrypted from mounts join disk_encryption on mounts.device_alias = disk_encryption.name where mounts.path = '/'",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-FileVault",
            "query_finished": macos_filevault_query_finished,
        },
        {
            "name": "Gatekeeper",
            "good_string": "Gatekeeper is enabled",
            "bad_string": "Gatekeeper should be enabled",
            "query": "select assessments_enabled from gatekeeper",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-Gatekeeper",
            "query_finished": macos_gatekeeper_query_finished,
        },
        {
            "name": "Firewall",
            "good_string": "Firewall is enabled",
            "bad_string": "Firewall should be enabled",
            "query": "select global_state from alf",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-Firewall",
            "query_finished": macos_firewall_query_finished,
        },
        {
            "name": "Remote sharing",
            "good_string": "Remote sharing is disabled",
            "bad_string": "Remote sharing should be disabled",
            "query": "select * from sharing_preferences",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-Remote-Sharing",
            "query_finished": macos_remote_sharing_query_finished,
        },
        {
            "name": "macOS automatic updates",
            "good_string": "macOS automatic updates are enabled",
            "bad_string": "macOS automatic updates should be enabled",
            "query": "select value from plist where path = '/Library/Preferences/com.apple.commerce.plist' and key = 'AutoUpdate'",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-macOS-Automatic-Updates",
            "query_finished": macos_automatic_updates_query_finished,
        },
        {
            "name": "Guest user",
            "good_string": "Guest user is disabled",
            "bad_string": "Guest user should be disabled",
            "query": "select value from plist where path='/Library/Preferences/com.apple.loginwindow.plist' and key='GuestEnabled'",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-Guest-User",
            "query_finished": macos_guest_user_query_finished,
        },
        {
            "name": "System Integrity Protection",
            "good_string": "System Integrity Protection is enabled",
            "bad_string": "System Integrity Protection should be enabled",
            "query": "select enabled from sip_config where config_flag='sip'",
            "help_url": "https://github.com/firstlookmedia/flock-agent/wiki/macOS-Health-Check:-System-Integrity-Protection",
            "query_finished": macos_sip_query_finished,
        },
    ],
    "linux": [],
}
