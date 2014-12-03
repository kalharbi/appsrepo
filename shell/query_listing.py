import sys
import os
import ConfigParser
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName

class QueryListing(object):
    """ Retreives data from the listing details collection in MongoDB.
    """
    config = ConfigParser.ConfigParser()

    def __init__(self):
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "appsrepo-shell.conf"))
        self.host_name = self.config.get('mongodb', 'host')
        self.port_number = self.config.get('mongodb', 'port')
        self.db_name = self.config.get('mongodb', 'db')
        self.collection_name = self.config.get('mongodb', 'listing_collection')

    def connect_mongodb(self):
        try:
            client = MongoClient(self.host_name, self.port_number)
            db = client[self.db_name]
            collection = db[self.collection_name]
            self.log.info("Connected to %s:%s, database: %s, Collection: %s.",
                          self.host_name, self.port_number, self.DB_NAME, self.BUCKET_NAME)
            return collection
        except ConnectionFailure:
            print("Connected to {host}:{port}, database: {db} Collection: {collection}. failed or is lost.".format(
                          host=self.host_name, port=self.port_number, db=self.db_name, collection=self.collection_name))
            sys.exit(1)
        except InvalidName:
            sys.exit("ERROR: Invalid database name, " + self.db_name + " .")

    def start_main(self, source_directory):
        # Connect to MongoDB
        collection = self.connect_mongodb()