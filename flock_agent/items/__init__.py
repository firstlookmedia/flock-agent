# -*- coding: utf-8 -*-
from .osquery import OsqueryItem
from .osquery_config import OsqueryConfigItem
from .openjdk import OpenJdkItem
from .logstash import LogstashItem
from .logstash_config import LogstashConfigItem

class ItemList(list):
    """
    An ordered list of all items
    """
    def __init__(self, display, config_path):
        super(list, self).__init__()

        # Add all of the items
        self.append( OsqueryItem(display, config_path) )
        self.append( OsqueryConfigItem(display, config_path) )
        self.append( OpenJdkItem(display, config_path) )
        self.append( LogstashItem(display, config_path) )
        self.append( LogstashConfigItem(display, config_path) )
