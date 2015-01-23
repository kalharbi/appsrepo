from py2neo import Graph
import configparser

class QueryUI:
    """ Retreives data from the UI in neo4j.
    """
    config = configparser.ConfigParser()
    
    def __init__(self):
        
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "appsrepo-shell.conf"))
        self.host_name = self.config.get('mongodb', 'host')
        self.port_number = int(self.config.get('mongodb', 'port'))
        self.db_name = self.config.get('mongodb', 'db')
        self.collection_name = self.config.get('mongodb', 'listing_collection')
        self.pp = pprint.PrettyPrinter()
        
    def __connect(self, host, port, db_path):
        address = "http://" + host + ":" + str(port) + db_path
        graph = Graph(address)
    
    def execute_query(self, query):
        return None
        
    def __execute_find_query(self, selection, fields = {}, sort_field = None, sort=1, limit=0):
        """ Find documents in a collection and returns a Cursor to the selected documents.
        The cursor is an iterable whose iterators cycle over the query results.
        
        Keyword arguments:
        selection -- A dict specifying the selection criteria.
        fields -- A dict specifying a projection set of fields to return.
        sort -- Specifies the order in which the query returns matching documents.
        It's an integer value of 1 or -1 to specify an ascending or descending sort respectively.
        """
        return None
        
        