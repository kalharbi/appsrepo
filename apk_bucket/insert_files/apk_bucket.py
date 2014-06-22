# !/usr/bin/python
import sys
import os
import datetime
import logging
import logging.handlers
from optparse import OptionParser
from subprocess import Popen, PIPE

from pymongo import MongoClient
import gridfs
from pymongo.errors import ConnectionFailure, InvalidName

import ConfigParser


class ApkBucket(object):
    """ This tool stores apk files into MongoDB using GridFS
    """

    DB_NAME = "apps"
    BUCKET_NAME = "apk"
    PORT_NUMBER = 27017
    HOST_NAME = "localhost"

    log = logging.getLogger("manifest_features")
    log.setLevel(
        logging.DEBUG)  # The logger's level must be set to the "lowest" level.
    config = ConfigParser.ConfigParser()

    def __init__(self):
        self.apk_files = []
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "apk_bucket.conf"))

    def connect_mongodb(self):
        try:
            client = MongoClient(self.HOST_NAME, self.PORT_NUMBER)
            db = client[self.DB_NAME]
            apk_bucket_collection = gridfs.GridFS(db, collection=self.BUCKET_NAME)
            self.log.info("Connected to database: %s Collection: %s.",
                          self.DB_NAME,
                          self.BUCKET_NAME)
            return apk_bucket_collection
        except ConnectionFailure:
            sys.exit("ERROR: Connection to the database failed or is lost.")
        except InvalidName:
            sys.exit("ERROR: Invalid database name")

    @staticmethod
    def document_exists(apk_bucket_collection, package_name, version_code):
        """ Check if the file exists in this apk_bukcet collection. """
        return apk_bucket_collection.exists(
            {"metadata.n": package_name, "metadata.verc": version_code})

    def start_main(self, source_directory):
        # Connect to MongoDB
        apk_bucket_collection = self.connect_mongodb()
        # Get all apk files and save them into a global variable named 'apk_files'
        self.find_apk_files(source_directory)
        for apk_file in self.apk_files:
            # Check file size
            stat_info = os.stat(apk_file)
            if(stat_info.st_size == 0):
                self.log.error("Empty APK file: %s", apk_file)
                continue
            app_info = self.get_app_info(apk_file)
            if app_info is None: continue
            additional_metadata = {"n": app_info["package_name"], "verc": app_info["version_code"],
                                   "vern": app_info["version_name"]}
            custom_file_name = app_info["package_name"] + "-" + app_info["version_code"] + "-" + app_info[
                "version_name"]
            print(additional_metadata)
            print(custom_file_name)
            if (self.document_exists(apk_bucket_collection, app_info["package_name"], app_info["version_code"])):
                self.log.info("APK file for package %s, version code: %s already exists.",
                              app_info["package_name"], app_info["version_code"])
                continue
            else:
                with open(apk_file) as new_apk_file:
                    inserted_file_id = apk_bucket_collection.put(new_apk_file, content_type='apk',
                                                                 filename=custom_file_name,
                                                                 metadata=additional_metadata)
                    self.log.info("Inserted a new APK file for package: %s, version code: %s", app_info["package_name"],
                                  app_info["version_code"])

    def get_app_info(self, apk_file):
        """ Returns package name, version code, and version name by running aapt on the apk file.
        """
        version_info = {}
        aapt_path = self.config.get('tools', 'aapt')
        sub_process = Popen([aapt_path, 'dump', 'badging', apk_file],
                            stdout=PIPE, stderr=PIPE)
        out, err = sub_process.communicate()
        if err:
            self.log.error("Failed to run aapt on %s. %s", apk_file, err)
            return None
        if out:
            for line in out.splitlines():
                segment = line.strip().split(':')
                if (segment is not None and len(segment) > 1):
                    if (segment[0] == "package"):
                        package_info = segment[1].strip().split(' ')
                        for info_line in package_info:
                            info = info_line.strip().split('=')
                            if (info[0] == "name"):
                                version_info['package_name'] = info[1].replace("'", "")
                            elif (info[0] == "versionCode"):
                                # Remove the ' character from the string value
                                version_info['version_code'] = info[1].replace("'", "")
                            elif (info[0] == "versionName"):
                                version_info['version_name'] = info[1].replace("'", "")
                        break
        return version_info

    def find_apk_files(self, source_directory):
        if (not os.path.exists(source_directory)):
            self.log.error(source_directory + ' No such file or directory.')
            return None

        self.files_listing(os.path.abspath(source_directory), '.apk')

        if len(self.apk_files) == 1:
            self.log.info('Found APK file:' + self.apk_files[0])
        elif len(self.apk_files) > 1:
            self.log.info('Found ' + str(len(self.apk_files)) + ' APK files.')
        elif len(self.apk_files) == 0:
            sys.exit('Could not find any APK file in: ' +
                     source_directory)

    def files_listing(self, source_directory, ext_name):
        for item in os.listdir(source_directory):
            file = os.path.join(source_directory, item)
            if (os.path.isdir(file)):
                self.log.info('searching for apk files in ' + file)
                self.files_listing(file, ext_name)
            elif (os.path.splitext(file)[1].lower() == ext_name):
                self.apk_files.append(file)

    def main(self, args):
        start_time = datetime.datetime.now()
        # Configure logging
        logging_file = None
        logging_level = logging.ERROR
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # Create console logger and set its formatter and level
        logging_console = logging.StreamHandler(sys.stdout)
        logging_console.setFormatter(formatter)
        logging_console.setLevel(logging.DEBUG)
        # Add the console logger
        self.log.addHandler(logging_console)

        # command line parser
        parser = OptionParser(usage="python %prog apk_files_directory [options]", version="%prog 1.0")
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
        source_dir = None
        if os.path.isdir(args[0]):
            source_dir = os.path.abspath(args[0])
        else:
            sys.exit("Error: source directory " + args[0] + " does not exist.")

        self.start_main(source_dir)

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    ApkBucket().main(sys.argv[1:])
