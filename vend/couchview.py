###
# Source: https://markhaa.se/couchdb-views-in-python.html
#
# Copyright 2012 Mark Haase. Used in good faith.
#
# Edited in 2020 by Beads Land-Trujillo to document CouchDB configuration and
# expose design and view names.
###

# To use, add the following to /opt/couchdb/bin/couchdb
#
#  COUCHDB_QUERY_SERVER_PYTHON = "/usr/local/bin/couchpy"
#
# Per: https://docs.couchdb.org/en/stable/config/query-servers.html
# Per: https://couchdb-python.readthedocs.io/en/latest/views.html

from couchdb.design import ViewDefinition
import inflection
import sys

class CouchView(ViewDefinition):
    """
    A base class for couch views that handles the magic of instantiation.
    """

    def __init__(self):
        """
        Does some magic to map the subclass implementation into the format
        expected by ViewDefinition.
        """

        module = sys.modules[self.__module__]
        self.design_name = module.__name__.split('.')[-1]
        self.view_name = inflection.underscore(self.__class__.__name__)

        if hasattr(self.__class__, "map"):
            map_fun = self.__class__.map
        else:
            raise NotImplementedError("Couch views require a map() method.")

        if hasattr(self.__class__, "reduce"):
            reduce_fun = self.__class__.reduce
        else:
            reduce_fun = None

        super_args = (self.design_name,
                      self.view_name,
                      map_fun,
                      reduce_fun,
                      'python')

        super(CouchView, self).__init__(*super_args)
