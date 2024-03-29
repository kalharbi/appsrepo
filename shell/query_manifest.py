import pprint
import sys
import os
import configparser
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName

class QueryManifest(object):
    """ Retreives data from the manifest collection in MongoDB.
    """
    config = configparser.ConfigParser()
    
    def __init__(self):
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "appsrepo-shell.conf"))
        self.host_name = self.config.get('mongodb', 'host')
        self.port_number = int(self.config.get('mongodb', 'port'))
        self.db_name = self.config.get('mongodb', 'db')
        self.collection_name = self.config.get('mongodb', 'manifest_collection')
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
        selection = {'package': package_name}
        if package_name == '*':
            selection = {}
        
        if features[0] == 'uses_permissions':
            fields = {'uses_permissions': 1, 'package': 1 ,'version_code': 1, 'version_name' : 1, '_id' : 0}
            cursor = None
            if version_index < 0:
                version_index = abs(version_index)
                cursor = self.__execute_find_query(selection, fields, 'version_code', -1, version_index)
            else:
                cursor = self.__execute_find_query(selection, fields, 'version_code', 1, version_index)
            if functions[0] == 'find()':
                permissions_list = self.__get_permissions(cursor)
                if len(functions) == 2 and functions[1] == 'diff()':
                    self.__print_diff_lists(permissions_list[0], permissions_list[-1])
            elif functions[0] == 'count()':
                permissions_count = self.__get_permissions_count(cursor)
                if len(functions) == 2 and functions[1] == 'diff()':
                    self.__print_diff_numbers(permissions_count)
            else:
                logging.error("Undefined function:  '%s' is not defined.", functions[0])
        else:
            if functions[0] == 'find()':
                fields = {'.'.join(features): 1, 'package': 1 ,'version_code': 1, 'version_name' : 1, '_id' : 0}
                cursor = self.__execute_find_query(selection, fields, 'version_code', 1, version_index)
                entries = cursor[:]
                self.__print_dict_entries(entries)
                if len(functions) == 2 and functions[1] == 'diff()':
                    cursor.rewind()
                    if cursor.count() > 1:
                        for x in range(0, cursor.count()):
                           if x != cursor.count() - 1:
                               self.__print_diff_lists(entries[x], entries[x+1])
            elif functions[0] == 'count()':
                fields = {'.'.join(features): 1, 'package': 1 ,'version_code': 1, 'version_name' : 1, '_id' : 0}
                cursor = self.__execute_find_query(selection, fields, 'version_code', 1, version_index)
                count = self.__get_dict_entries_count(cursor, features[0])
                if len(functions) == 2 and functions[1] == 'diff()':
                    self.__print_diff_numbers(count)
                
                        
            
    
    def __get_permissions(self, cursor):
        permissions_list = []
        if cursor is not None and cursor.count() > 0:
            for entry in cursor:
                print(entry['package'] + ", version_code: " + entry['version_code'] +
                      ", version_name: " + entry['version_name'])
                permissions = entry['uses_permissions']
                ver_perm_list = []
                for permission in permissions:
                    print(permission['name'])
                    ver_perm_list.append(permission['name'])
                permissions_list.append(ver_perm_list)
        return permissions_list
    
    def __get_permissions_count(self, cursor):
        permissions_count = []
        if cursor is not None and cursor.count() > 0:
            for entry in cursor:
                permissions = entry['uses_permissions']
                print(entry['package'] + ", version_code: " + entry['version_code'] +
                      ", version_name: " + entry['version_name'] +  ", total_permissions: " +
                      str(len(permissions)))
                permissions_count.append(len(permissions))
        
        return permissions_count
        
    def __print_diff_numbers(self, l):
        print("Diff: " + str(l[-1] - l[0]))
    
    def __print_diff_lists(self, l1, l2):
        print("+ ")
        added = set(l2) - set(l1)
        for value in added:
            print(value)
        print("-")
        removed = set(l1) - set(l2)
        for value in removed:
            print(value)
    
    def __print_diff_dicts(self, d1, d2):
        print("+ ")
        added = set(d2.values()) - set(d1.values)
        for value in added:
            print(value)
        print("-")
        removed = set(d1.values()) - set(d2.values)
        for value in removed:
            print(value)
    
    def __print_dict_entries(self, entries):
        for entry in entries:
            print(entry['package'] + ", version_code: " + entry['version_code'] +
                  ", version_name: " + entry['version_name'])
            self.pp.pprint(entry)
            
    def __get_dict_entries_count(self, entries, key):
        entries_count = []
        for entry in entries:
            print(entry['package'] + ", version_code: " + entry['version_code'] +
                  ", version_name: " + entry['version_name'] +  ", total: " +
                  str(len(entry[key])))
            entries_count.append(len(entry[key]))
        return entries_count
        