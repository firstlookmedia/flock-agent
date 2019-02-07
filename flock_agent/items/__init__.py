# -*- coding: utf-8 -*-
from .osquery import OsqueryItem
from .osquery_config import OsqueryConfigItem
from .openjdk import OpenJdkItem
from .logstash import LogstashItem

class ItemList(list):
    """
    An ordered list of all items
    """
    def __init__(self, agent):
        super(list, self).__init__()

        # Add all of the items
        self.append( OsqueryItem(agent) )
        self.append( OsqueryConfigItem(agent) )
        self.append( OpenJdkItem(agent) )
        self.append( LogstashItem(agent) )
