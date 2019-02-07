# -*- coding: utf-8 -*-
from .osquery import OsqueryItem


class ItemList(list):
    """
    An ordered list of all items
    """
    def __init__(self, agent):
        super(list, self).__init__()

        # Add all of the items
        self.append( OsqueryItem(agent) )
