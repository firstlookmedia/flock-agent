# -*- coding: utf-8 -*-

# A type of data that Flock Agent collects via osquery, and sends to a Flock
# server, is called a "twig". This file hard-codes all of the available twigs,
# and users have the option to opt-out of individual twigs.

twigs = {
    # Relevant twigs from the vuln-management query pack
    # https://github.com/facebook/osquery/blob/experimental/packs/vuln-management.conf

    "os_version": {
        "name": "macOS version",
        "query": "select * from os_version;",
        "interval": 86400,
        "description": "The current version of macOS that's on your computer'"
    },
    "browser_plugins": {
        "name": "Browser plugins",
        "query": "select browser_plugins.* from users join browser_plugins using (uid);",
        "interval": 86400,
        "description": "List of browser plugins, which can allow us to detect if you have malicious ones installed"
    },
    "safari_extensions": {
        "name": "Safari extensions",
        "query": "select safari_extensions.* from users join safari_extensions using (uid);",
        "interval": 86400,
        "description": "List of Safari extensions, which can allow us to detect if you have malicious ones installed"
    },
    "opera_extensions": {
        "name": "Opera extensions",
        "query": "select opera_extensions.* from users join opera_extensions using (uid);",
        "interval": 86400,
        "description": "List of Opera extensions, which can allow us to detect if you have malicious ones installed"
    },
    "chrome_extensions": {
        "name": "Chrome extensions",
        "query": "select chrome_extensions.* from users join chrome_extensions using (uid);",
        "interval": 86400,
        "description": "List of Chrome extensions, which can allow us to detect if you have malicious ones installed"
    },
    "firefox_addons": {
        "name": "Firefox add-ons",
        "query": "select firefox_addons.* from users join firefox_addons using (uid);",
        "interval": 86400,
        "description": "List of Safari extensions, which can allow us to detect if you have malicious ones installed"
    },

    # Relevant twigs from the incident-response query pack
    # https://github.com/facebook/osquery/blob/experimental/packs/incident-response.conf

    "launchd": {
        "name": "Launch daemons",
        "query": "select * from launchd;",
        "interval": 3600,
        "description": "What daemons (background services) automatically start on your computer, which malware could use for persistence"
    },
    "startup_items": {
        "name": "Startup items",
        "query": "select * from startup_items;",
        "interval": 86400,
        "description": "What apps automatically start on your computer, which malware could use for persistence"
    },
    "crontab": {
        "name": "Scheduled tasks (cron jobs)",
        "query": "select * from crontab;",
        "interval": 3600,
        "description": "What programs are scheduled to run at regular intervals, which malware could use for persistence"
    },
    "loginwindow1": {
        "name": "Login window values",
        "query": "select key, subkey, value from plist where path = '/Library/Preferences/com.apple.loginwindow.plist';",
        "interval": 86400,
        "description": "What loginwindow values are set, including if the guest user is enabled, and which malware could use for persistence on system boot"
    },
    # "loginwindow2": {
    #     "name": "Login window values (2)",
    #     "query": "select key, subkey, value from plist where path = '/Library/Preferences/loginwindow.plist';",
    #     "interval": 86400,
    #     "description": "What loginwindow values are set, which malware could use for persistence on system boot"
    # },
    # "loginwindow3": {
    #     "name": "Login window values (3)",
    #     "query": "select username, key, subkey, value from plist p, (select * from users where directory like '/Users/%') u where p.path = u.directory || '/Library/Preferences/com.apple.loginwindow.plist';",
    #     "interval": 86400,
    #     "description": "What loginwindow values are set, which malware could use for persistence on system boot"
    # },
    # "loginwindow4": {
    #     "name": "Login window values (4)",
    #     "query": "select username, key, subkey, value from plist p, (select * from users where directory like '/Users/%') u where p.path = u.directory || '/Library/Preferences/loginwindow.plist';",
    #     "interval": 86400,
    #     "description": "What loginwindow values are set, which malware could use for persistence on system boot"
    # },
    "alf": {
        "name": "Application firewall configuration",
        "query": "select * from alf;",
        "interval": 3600,
        "description": "How the application firewall is configured"
    },
    # "alf_exceptions": {
    #     "name": "Application firewall exceptions",
    #     "query": "select * from alf_exceptions;",
    #     "interval": 3600,
    #     "description": "Exceptions to the application firewall, allowing us to identify unwanted firewall holes made by malware or humans"
    # },
    "alf_services": {
        "name": "Application firewall services",
        "query": "select * from alf_services;",
        "interval": 3600,
        "description": "Which network services are allowed through the firewall, allowing us to identify unwanted firewall holes made by malware or humans"
    },
    # "alf_explicit_auths": {
    #     "name": "Application firewall explicit authorizations",
    #     "query": "select * from alf_explicit_auths;",
    #     "interval": 3600,
    #     "description": "Processes with explicit authorization for the application firewall, allowing us to identify unwanted firewall holes made by malware or humans"
    # },
    "etc_hosts": {
        "name": "Local hostnames",
        "query": "select * from etc_hosts;",
        "interval": 86400,
        "description": "Values from the /etc/hosts file, which could be used to redirect or block network communications"
    },
    "kextstat": {
        "name": "Kernel extensions",
        "query": "select * from kernel_extensions;",
        "interval": 3600,
        "description": "What current kernel extensions are loaded; some malware has a kernel expension component and this could help us catch it"
    },
    # "last": {
    #     "name": "Most recent logins",
    #     "query": "select * from last;",
    #     "interval": 3600,
    #     "description": "A list of the most recent time which users have logged into your computer, which will help use verify assumptions of what accounts should be accessing what computers, and identify computers accessed during a compromise"
    # },
    "installed_applications": {
        "name": "Installed applications",
        "query": "select * from apps;",
        "interval": 3600,
        "description": "List of applications that are currently installed, to help identify malware, adware, or vulnerable applications that are installed"
    },
    # "open_sockets": {
    #     "name": "Open network connections",
    #     "query": "select distinct pid, family, protocol, local_address, local_port, remote_address, remote_port, path from process_open_sockets where path <> '' or remote_address <> '';",
    #     "interval": 86400,
    #     "description": "List of all the open network sockets per process, which could help identify connections to known-bad IP addresses, or odd local or remote port bindings"
    # },
    # "logged_in_users": {
    #     "name": "Logged in users",
    #     "query": "select liu.*, p.name, p.cmdline, p.cwd, p.root from logged_in_users liu, processes p where liu.pid = p.pid;",
    #     "interval": 3600,
    #     "description": "List of all the currently logged in users, which is useful for intrusion detection and incident response"
    # },
    # "ip_forwarding": {
    #     "name": "IP forwarding",
    #     "query": "select * from system_controls where oid = '4.30.41.1' union select * from system_controls where oid = '4.2.0.1';",
    #     "interval": 3600,
    #     "description": "The current status of IP forwarding, which can determine if your computer is being used as a network relay"
    # },
    # "ramdisk": {
    #     "name": "RAM disks",
    #     "query": "select * from block_devices where type = 'Virtual Interface';",
    #     "interval": 3600,
    #     "platform": "posix",
    #     "version": "1.4.5",
    #     "description": "A list of ramdisks currently mounted, which an attacker might use to avoid touching the disk for anti-forensics purposes"
    # },
    # "listening_ports": {
    #     "name": "Listening ports",
    #     "query": "select * from listening_ports;",
    #     "interval": 3600,
    #     "description": "List of network ports that are listening for incoming connections, which malware could use for remote access"
    # },
    "suid_bin": {
        "name": "Setuid binaries",
        "query": "select * from suid_bin;",
        "interval": 3600,
        "description": "List of binary files on your computer with setuid enabled, which could be used for privilege escelation, including privilege escelation backdoors"
    },
    # "arp_cache": {
    #     "name": "ARP cache",
    #     "query": "select * from arp_cache;",
    #     "interval": 3600,
    #     "description": "A copy of the ARP cache values, which could detect if a local man-in-the-middle attack is in progress"
    # },
    "disk_encryption": {
        "name": "Disk encryption",
        "query": "select * from disk_encryption;",
        "interval": 86400,
        "description": "Whether disk encryption is enabled"
    },

    # Detect reverse shells
    # https://clo.ng/blog/osquery_reverse_shell/

    "reverse_shell": {
        "name": "Reverse shells",
        "query": "SELECT DISTINCT(processes.pid), processes.parent, processes.name, processes.path, processes.cmdline, processes.cwd, processes.root, processes.uid, processes.gid, processes.start_time, process_open_sockets.remote_address, process_open_sockets.remote_port, (SELECT cmdline FROM processes AS parent_cmdline WHERE pid=processes.parent) AS parent_cmdline FROM processes JOIN process_open_sockets USING (pid) LEFT OUTER JOIN process_open_files ON processes.pid = process_open_files.pid WHERE ( name='sh' OR name='bash' ) AND process_open_files.pid IS NULL;",
        "interval": 600,
        "description": "Detect reverse shells, which is the first step attackers often take after an initial compromise in order to more easily run commands on your computer"
    }
}
