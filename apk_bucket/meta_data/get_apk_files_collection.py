# !/usr/bin/python
import sys
import os
import datetime
import logging
import logging.handlers
from optparse import OptionParser

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName

import ConfigParser


class ApkNamesRretrieval(object):

    """ This tool retrieves all files metadata from MongoDB GridFS files collection.
    """

    DB_NAME = "apps"
    COLLECTION_NAME = "apk.files"
    PORT_NUMBER = 27017
    HOST_NAME = "localhost"

    log = logging.getLogger("apk_files_retrieval")
    log.setLevel(
        logging.DEBUG)  # The logger's level must be set to the "lowest" level.

    def __init__(self):
        self.target_directroy = None

    def connect_mongodb(self):
        try:
            client = MongoClient(self.HOST_NAME, self.PORT_NUMBER)
            db = client[self.DB_NAME]
            apk_bucket_files_collection = db[self.COLLECTION_NAME]
            self.log.info("Connected to database: %s Collection: %s.",
                          self.DB_NAME,
                          self.COLLECTION_NAME)
            return apk_bucket_files_collection
        except ConnectionFailure:
            sys.exit("ERROR: Connection to the database failed or is lost.")
        except InvalidName:
            sys.exit("ERROR: Invalid database name")

    def find_all_fields(self):
        # Connect to MongoDB
        apk_bucket_files_collection = self.connect_mongodb()
        # Result file
        result_file_name = os.path.join(
            self.target_directory, "apk_files_collection.csv")
        result_file = open(result_file_name, 'w')
        result_file.write('package_name, version_code\n')
        self.retrieve_metadata_from_collection(apk_bucket_files_collection, result_file)
        result_file.close()
        
    def retrieve_metadata_from_collection(self, fs_collection, result_file):
        self.log.info("Retrieving all package names and version code values in the apk.files collection.")

        cursor = fs_collection.find({})
        if cursor.count() > 0:
            for entry in cursor:
                metadata = entry['metadata']
                line = metadata['n'] + ',' + metadata['verc'] + '\n'
                self.log.info(line)
                result_file.write(line)
        else:
            self.log.error(
                "Could not find any documents in the apk.files collection.")

    def main(self, args):
        start_time = datetime.datetime.now()
        # Configure logging
        logging_file = None
        logging_level = logging.ERROR
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        # Create console logger and set its formatter and level
        logging_console = logging.StreamHandler(sys.stdout)
        logging_console.setFormatter(formatter)
        logging_console.setLevel(logging.DEBUG)
        # Add the console logger
        self.log.addHandler(logging_console)

        # command line parser
        usage_info = '''
        python %prog target_directory [options]\n
        Retrieves all package name and version code values for the documents stored in apk.files collection and saves them into target_directory.
        '''
        parser = OptionParser(usage=usage_info, version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='increase verbosity.')

        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("Invalid number of arguments.")

        if options.log_file:
            logging_file = logging.FileHandler(options.log_file, mode='a',
                                               encoding='utf-8', delay=False)
            logging_file.setLevel(logging_level)
            logging_file.setFormatter(formatter)
            self.log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]

            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)

        # Check target directory
        if os.path.isdir(args[0]):
            self.target_directory = os.path.abspath(args[0])
        else:
            sys.exit(
                "Error: target directory " + args[0] + " does not exist.")
        self.find_all_fields()
        
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    ApkNamesRretrieval().main(sys.argv[1:])
