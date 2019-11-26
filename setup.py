#!/usr/bin/env python3
import setuptools
import os
import sys
from flock_agent import flock_agent_version


def file_list(path):
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            files.append(os.path.join(path, filename))
    return files


setuptools.setup(
    name="flock-agent",
    version=flock_agent_version,
    author="Micah Lee",
    author_email="micah.lee@firstlook.org",
    description="Agent for Flock, the privacy-preserving fleet management system",
    long_description="Agent for Flock, the privacy-preserving fleet management system. The goal of Flock is to gain visibility into a fleet of workstation computers while protecting the privacy of their users. It achieves this by only collecting information needed to inform security decisions, and by not allowing the IT team to access arbitrary files or execute arbitrary code on the computers they are monitoring.",
    url="https://github.com/firstlookmedia/flock-agent",
    packages=[
        "flock_agent",
        "flock_agent.daemon",
        "flock_agent.gui",
        "flock_agent.gui.tabs",
        "flock_agent.gui.requests_unixsocket",
    ],
    data_files=[
        (
            os.path.join(sys.prefix, "share/applications"),
            ["share/autostart/linux/media.firstlook.flock-agent.desktop"],
        ),
        (
            os.path.join(sys.prefix, "share/icons/hicolor/64x64/apps"),
            ["install/linux/media.firstlook.flock-agent.png"],
        ),
        (
            os.path.join(sys.prefix, "share/flock-agent/images"),
            file_list("share/images"),
        ),
        (
            os.path.join(sys.prefix, "share/flock-agent/autostart/linux"),
            file_list("share/autostart/linux"),
        ),
        ("/etc/systemd/system", ["install/linux/flock-agent.service"]),
    ],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
    ),
    entry_points={"console_scripts": ["flock-agent = flock_agent:main"]},
)
