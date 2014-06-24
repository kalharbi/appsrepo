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


class ApkMetadataRretrieval(object):

    """ This tool retrieves files metadata from MongoDB GridFS files collection.
    """

    DB_NAME = "apps"
    COLLECTION_NAME = "apk.files"
    PORT_NUMBER = 27017
    HOST_NAME = "localhost"

    log = logging.getLogger("files_metadata")
    log.setLevel(
        logging.DEBUG)  # The logger's level must be set to the "lowest" level.
    config = ConfigParser.ConfigParser()

    def __init__(self):
        self.config.read(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "config", "apk_bucket.conf"))
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

    def find_using_file(self, list_file):
        self.log.info("Reading file: %s", list_file)
        # Connect to MongoDB
        apk_bucket_files_collection = self.connect_mongodb()
        # Result file
        result_file_name = os.path.join(
            self.target_directory, "files_info.csv")
        result_file = open(result_file_name, 'w')
        result_file.write(
            '"package_name", "version_code", "length_in_bytes" \n')
        with open(list_file, 'r') as f:
            # skip the first line since it's the header line [package_name,
            # version_code]
            next(f)
            for line in f:
                try:
                    arr = [items.strip() for items in line.split(',')]
                    package_name = arr[0]
                    version_code = arr[1]
                    if package_name and version_code:
                        self.retrieve_metadata_from_collection(apk_bucket_files_collection, package_name, version_code,
                                                               result_file)
                    else:
                        self.log.error("Missing info: %s", line)
                except IndexError as e:
                    self.log.error("Error while reading CSV file. %s", e)
        result_file.close()

    def find_using_package_values(self, package_name, version_code):
        # Connect to MongoDB
        apk_bucket_files_collection = self.connect_mongodb()
        # Result file
        result_file_name = os.path.join(
            self.target_directory, "files_info.csv")
        result_file = open(result_file_name, 'w')
        result_file.write(
            '"package_name", "version_code", "length_in_bytes" \n')
        self.retrieve_metadata_from_collection(
            apk_bucket_files_collection, package_name, version_code, result_file)
        result_file.close()

    def retrieve_metadata_from_collection(self, fs_collection, package_name, version_code, result_file):
        self.log.info("Retrieving metadata info for package: " +
                      package_name + ", version code: " + version_code)

        cursor = fs_collection.find(
            {"metadata.n": package_name, "metadata.verc": version_code}, {'length': 1}).limit(1)
        if cursor.count() > 0:
            for entry in cursor:
                length_in_bytes = entry['length']
                line = package_name + ',' + version_code + \
                    ',' + str(length_in_bytes) + '\n'
                self.log.info(line)
                result_file.write(line)
        else:
            self.log.error(
                "Could not find the APK file for package:%s, version code:%s", package_name, version_code)

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
        python %prog { {<package_name> <version_code>} | <list_file> } target_directory [options]\n
        Retrieves files metadata from MongoDB GridFS files collection and saves them into target_directory.
        Metadata includes: length (the size in bytes).
        
        package_name: Android app package name.
        version_code: Android app version code value.
        list_file: A CSV file that contains package names and version code numbers.\n
        Example:
        python %prog com.evernote 1057013
        
        OR
        
        python %prog list_file.csv
        list_file.csv:
                      package_name,version_code
                      com.evernote,1057013
                      .....\n
        '''
        parser = OptionParser(usage=usage_info, version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='increase verbosity.')

        (options, args) = parser.parse_args()
        target_directory = None
        list_file = None
        package_name = None
        version_code = None

        if len(args) == 2:
            list_file = args[0]
            if os.path.exists(list_file):
                list_file = os.path.abspath(args[0])
            else:
                sys.exit("list_file " + list_file + " does not exist.")
            target_directory = args[1]
        elif len(args) == 3:
            package_name = args[0]
            version_code = args[1]
            target_directory = args[2]
        else:
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
        if os.path.isdir(target_directory):
            self.target_directory = os.path.abspath(target_directory)
        else:
            sys.exit(
                "Error: target directory " + target_directory + " does not exist.")

        if len(args) == 2:
            self.find_using_file(list_file)
        elif len(args) == 3:
            self.find_using_package_values(package_name, version_code)

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    ApkMetadataRretrieval().main(sys.argv[1:])
