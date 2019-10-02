# -*- coding: utf-8 -*-
from .global_settings import GlobalSettings
from .osquery import Osquery


def main(common):
    # Create an osquery object
    osquery = Osquery(common)

    # Load settings
    global_settings = GlobalSettings(common)

    print("Daemon not implemented yet")