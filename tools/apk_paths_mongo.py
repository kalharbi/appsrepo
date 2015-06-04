#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import ConfigParser
from optparse import OptionParser
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName
from subprocess import Popen, PIPE

class APKPathsMongo(object):
    """
    Recursively search for apk files and write their absolute paths, package
    names, and version info to a MongoDB collection named apk_paths.
    """
    log = logging.getLogger("apkFinder_log")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "config", "tools.conf"))

    def __init__(self):
        self.host_name = "localhost"
        self.port_number = 27017
        self.db_name = 'apps'
        self.collection_name = 'apk_paths'
        self.aapt_path = self.config.get('tools', 'aapt')

    # Returns a tuple containing the package, version code, and version name.
    def get_apk_info(self, apk_path):
        """ Returns package name, version code, and version name by
            running aapt on the apk file.
        """
        sub_process = None
        out = None
        err = None
        try:

            sub_process = Popen([self.aapt_path, 'dump', 'badging', apk_path],
                                stdout=PIPE, stderr=PIPE)
            out, err = sub_process.communicate()
        except OSError:
            print('Error: aapt tool is not defined in the config file at: ' +
                  './config/tools.conf')
            sys.exit(-1)
        version_info = {}
        if out:
            for line in out.split('\n'):
                segment = line.strip().split(":")
                if segment is not None and len(segment) > 0:
                    if segment[0] == "package":
                        package_info = segment[1].strip().split(' ')
                        for info_line in package_info:
                            info = info_line.strip().split('=')
                            if info[0] == "name":
                                version_info['package_name'] = info[1].replace("'", "")
                            elif info[0] == 'versionCode':
                                version_info['version_code'] = info[1].replace("'", "")
                            elif info[0] == 'versionName':
                                version_info['version_name'] = info [1].replace("'", "")
                        break
        # Return a hash of version code and version name
        return version_info

    def connect_mongodb(self):
        try:
            client = MongoClient(self.host_name, self.port_number)
            db = client[self.db_name]
            apk_files_collection = db[self.collection_name]
            self.log.info("Connected to %s:%s, database: %s, Collection: %s.",
                          self.host_name, self.port_number, self.db_name,
                          self.collection_name)
            return apk_files_collection
        except ConnectionFailure:
            print("Connected to {host}:{port}, database: {db}" +
                  " Collection: {collection}. failed or is lost.".format(
                      host=self.host_name, port=self.port_number,
                      db=self.db_name, collection=self.collection_name))
            sys.exit(1)
        except InvalidName:
            sys.exit("ERROR: Invalid database name")

    def insert_apk_path(self, apk_file, apk_paths_collection):
        if not os.path.exists(apk_file):
            self.error("APK file: %s does not exist", apk_file)
            return
        self.log.info('Found apk file %s', apk_file)
        app_info = self.get_apk_info(apk_file)
        if app_info is None or app_info["package_name"] is None \
                or app_info["version_code"] is None:
            self.log.error(
                'Failed to find version info for APK file %s',
                apk_file)
            return

        if self.document_exists(apk_paths_collection,
                                app_info["package_name"],
                                app_info["version_code"]):
            self.log.info("APK file for package %s, version code: %s "
                          + "already exists.",
                          app_info["package_name"],
                          app_info["version_code"])
            return
        else:
            # insert the path to mongodb collection
            doc = {'n': app_info["package_name"],
                   'verc': app_info["version_code"],
                   'vern': app_info["version_name"],
                   'size': self.get_file_size(apk_file),
                   'path': apk_file}
            doc_id = apk_paths_collection.insert(doc)
            self.log.info("A new document (Id: %s) containing " +
                          "metadata for  %s. has been inserted " +
                          "in collection: %s",
                          doc_id, apk_file, self.collection_name)

    def get_apk_paths(self, source_directory, apk_paths_collection):
        for item in os.listdir(source_directory):
            file = os.path.join(source_directory, item)
            if os.path.isdir(file):
                self.log.info('searching for apk files in ' + file)
                self.get_apk_paths(file)
            elif os.path.splitext(file)[1].lower() == ".apk":
                apk_file = os.path.abspath(file)
                self.insert_apk_path(apk_file, apk_paths_collection)

    @staticmethod
    def document_exists(apk_collection, package_name, version_code):
        """ Check if the file exists in this apk_paths collection. """
        if (apk_collection.find(
                {"n": package_name,
                 "verc": version_code}).count() > 0):
            return True
        else:
            return False

    @staticmethod
    def get_file_size(file):
        stat_info = os.stat(file)
        return stat_info.st_size

    def main(self, args):
        start_time = datetime.datetime.now()
        # Configure logging
        logging_file = None
        logging_level = logging.ERROR
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s' +
                                      ' - %(message)s')
        # Create console logger and set its formatter and level
        logging_console = logging.StreamHandler(sys.stdout)
        logging_console.setFormatter(formatter)
        logging_console.setLevel(logging.DEBUG)
        # Add the console logger
        self.log.addHandler(logging_console)

        # command line parser
        parser = OptionParser(usage="%prog [options] {apk_directory | apk_paths_file}",
                              description="%prog -- Recursively searches for apk files in" \
                                          "search_directory and writes their absoulte paths. package names, " \
                                          "version codes to a collection named apk_paths.",
                              version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            logging_file = logging.FileHandler(options.log_file, mode='a',
                                               encoding='utf-8', delay=False)
            logging_file.setLevel(logging_level)
            logging_file.setFormatter(formatter)
            self.log.addHandler(logging_file)
        input_source = os.path.abspath(args[0])
        if not os.path.exists(input_source):
            sys.exit("Error: " + input_source + " does not exist.")

        apks_collection = self.connect_mongodb()
        if os.path.isfile(input_source):
            with open(input_source, 'r') as f:
                for line in f:
                    line = line.strip()
                    self.insert_apk_path(line, apks_collection)
        elif os.path.isdir(input_source):
            self.get_apk_paths(input_source, apks_collection)

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    APKPathsMongo().main(sys.argv[1:])
