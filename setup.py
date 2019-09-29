import setuptools
import os
import sys
from flock_agent import flock_agent_version


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flock-agent",
    version=flock_agent_version,
    author="Micah Lee",
    author_email="micah.lee@firstlook.org",
    description="Join a privacy-preserving, centrally-managed Flock fleet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/firstlookmedia/flock-agent",
    packages=[
        'flock_agent',
        'flock_agent.gui',
        'flock_agent.gui.tabs'
    ],
    package_data={'flock_agent': ['share/*']},
    data_files=[
        (os.path.join(sys.prefix, 'share/applications'), ['share/autostart/linux/media.firstlook.flock-agent.desktop']),
        (os.path.join(sys.prefix, 'share/icons/hicolor/64x64/apps'), ['install/media.firstlook.flock-agent.png'])
    ],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent"
    ),
    entry_points={
        'console_scripts': [
            'flock-agent = flock_agent:main',
        ],
    },
)
