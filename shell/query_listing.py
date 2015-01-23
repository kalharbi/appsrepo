import sys
import os
import pprint
import configparser
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName

class QueryListing(object):
    """ Retreives data from the listing details collection in MongoDB.
    """
    config = configparser.ConfigParser()            
    listing_features = {'title' : 't', 'play_store_url' : 'url', 
                'category' : 'cat', 'price':'pri', 'date_published': 'dtp',
                'version_name' : 'vern', 'version_code':'verc',
                'operating_systems' : 'os', 'ratings_count' : 'rct',
                'rating' : 'rate', 'content_rating':'crat',
                'creator' : 'crt', 'creator_url' : 'curl', 
                'install_size' : 'sz', 'install_size_text' : 'sztxt', 
                'downloads_count' : 'dct', 'downloads_count_text' : 'dtxt',
                 'description' : 'desc', 'reviews' : 'rev', 'used_permissions':'per', 
                 'what_is_new': 'new'}
    
    def __init__(self):
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "appsrepo-shell.conf"))
        self.host_name = self.config.get('mongodb', 'host')
        self.port_number = int(self.config.get('mongodb', 'port'))
        self.db_name = self.config.get('mongodb', 'db')
        self.collection_name = self.config.get('mongodb', 'listing_collection')
        self.pp = pprint.PrettyPrinter()

    def __connect_mongodb(self):
        try:
            client = MongoClient(self.host_name, self.port_number)
            db = client[self.db_name]
            collection = db[self.collection_name]
            return collection
        except ConnectionFailure:
            print("Connected to {host}:{port}, database: {db} Collection: {collection}. failed or is lost.".format(
                          host=self.host_name, port=self.port_number, db=self.db_name, collection=self.collection_name))
            sys.exit(1)
        except InvalidName:
            sys.exit("ERROR: Invalid database name, " + self.db_name + " .")
    
    def __execute_find_query(self, selection, fields = {}, sort_field = None, sort=1, limit=0):
        """ Find documents in a collection and returns a Cursor to the selected documents.
        The cursor is an iterable whose iterators cycle over the query results.
        
        Keyword arguments:
        selection -- A dict specifying the selection criteria.
        fields -- A dict specifying a projection set of fields to return.
        sort -- Specifies the order in which the query returns matching documents.
        It's an integer value of 1 or -1 to specify an ascending or descending sort respectively.
        """
        cursor = None
        # Connect to MongoDB
        collection = self.__connect_mongodb()
        # set sort order
        sort_order = pymongo.ASCENDING
        if sort == -1:
            sort_order = pymongo.DESCENDING
        # Execute find query
        if sort_field is not None:
            cursor = collection.find(selection, fields).sort(sort_field, sort_order).limit(limit)
        elif limit > 0:
            cursor = collection.find(selection, fields).limit(limit)
        else:
            cursor = collection.find(selection, fields)
        return cursor
        
    def execute_query(self, package_name, version_index, features, functions):
        selection = {'n': package_name}
        if package_name == '*':
            selection = {}
        if functions[0] == 'find()':
            translated_features = self.__translate_features(features)
            if not translated_features:
                return
            fields = {'.'.join(translated_features): 1, 'n': 1 ,'verc': 1, 'vern' : 1, '_id' : 0}
            cursor = self.__execute_find_query(selection, fields, 'verc', 1, version_index)
            entries = cursor[:]
            self.__print_dict_entries(entries)
            if len(functions) == 2 and functions[1] == 'diff()':
                cursor.rewind()
                if cursor.count() > 1:
                    for x in range(0, cursor.count()):
                       if x != cursor.count() - 1:
                           self.__print_diff_lists(entries[x], entries[x+1])
                           
    def __translate_features(self, features):
        translated_features = []
        try:
            if len(features) > 1 and '.' in features:
                for f in features.split('.'):
                    translated_features.append(QueryListing.listing_features[f])
            elif len(features) == 1 and not '.' in features:
                translated_features.append(QueryListing.listing_features[features[0]])
        except KeyError:
            print("Unknown feature {}", feature_name)
            return None
        return translated_features
            
        
    def __print_dict_entries(self, entries):
        for entry in entries:
            #print(entry['n'] + ", version_code: " + str(entry['verc']) +
             #     ", version_name: " + str(entry['vern']))
            self.pp.pprint(entry)
            return
    
    def __print_diff_lists(self, l1, l2):
        print("+ ")
        added = set(l2) - set(l1)
        for value in added:
            print(value)
        print("-")
        removed = set(l1) - set(l2)
        for value in removed:
            print(value)