#!/usr/bin/python
import sys
import os.path
import json
import glob
import time
import yaml
import logging
import logging.handlers
from pymongo import MongoClient
from optparse import OptionParser
from manifest_parser import ManifestParser
from custom_json_encoder import CustomJsonEncoder

"""
This script parses AndroidManifest.xml files and stores them in MongoDB.

"""
class ManifestFeatures(object):
    
    DB_NAME = "apps"
    COLLECTION_NAME = "manifest"
    PORT_NUMBER = 27017
    HOST_NAME = "localhost"
    DIR_DEPTH_SEARCH = 1 # The depth of the directory listing for AndroidManifest.xml
    log = logging.getLogger("manifest_features")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
    
    def connect_mongodb(self):
        try:
            client = MongoClient(self.HOST_NAME, self.PORT_NUMBER)
            db = client[self.DB_NAME]
            manifest_collection = db[self.COLLECTION_NAME]
            self.log.info("Connected to database: %s Collection: %s.",self.DB_NAME,
                  self.COLLECTION_NAME)
            return manifest_collection
        except ConnectionFailure:
            sys.exit("ERROR: Connection to the database failed or is lost.")
        except InvalidName:
            sys.exit("ERROR: Invalid database name")
    
    def document_exists(self, manifest_collection, app_manifest):
        return manifest_collection.find_one({"package": app_manifest.package,
                                             "version_name" : app_manifest.version_name})
    
    def start_main(self, dir_name):
        manifest_collection = self.connect_mongodb()
        manifest_files = self.getManifestFiles(dir_name)
        for manifest_file in manifest_files:
            self.log.info("Processing file: %s.", manifest_file)
            app_manifest = ManifestParser().parse((manifest_file))
            apktool_yaml_file = os.path.join(os.path.dirname(manifest_file), 'apktool.yml')
            app_sdk_versions = self.get_app_sdk_versions(apktool_yaml_file)
            app_manifest.set_sdk_versions(app_sdk_versions[0], app_sdk_versions[1])
            if(self.document_exists(manifest_collection, app_manifest)):
                self.log.info("Already Exists.")
                continue
            else:
                json_manifest = json.dumps(app_manifest, indent=2, cls=CustomJsonEncoder)
                manifest_collection.insert(json.loads(json_manifest))
                self.log.info("Inserted a new document for apk: %s; version:%s", 
                              app_manifest.package, app_manifest.version_name)
        if(len(manifest_files) == 0):
            self.log.error("Error: Failed to find AndroidManifest.xml files in %s" +
                           " in the depth of %d directories.\nTry to change the depth" +
                           " value using the command line option -d",
                           dir_name, self.DIR_DEPTH_SEARCH)
    
    def get_app_sdk_versions(self, yaml_file):
        # Read apktool.yaml to get the min and target sdk versions
        try:
            self.log.info("Processing file %s.", yaml_file)
            with open(yaml_file, 'r') as f:
                doc = yaml.load(f)
            min_sdk_version = doc.get('sdkInfo', None).get('minSdkVersion', None)
            target_sdk_version = doc.get('sdkInfo', None).get('targetSdkVersion', None)
            return(min_sdk_version, target_sdk_version)
        except yaml.YAMLError, exc:
            self.log.error("Error in apktool yaml file:", exc)
            
    def main(self, argv):
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
        parser = OptionParser(usage="%prog [options] apk_dir ", version="%prog 1.0", description = 'The manifest_features tool recursively searches for a directory of unpacked apk files, parses their AndroidManifest.xml files and stores them in a MongoDB collection named manifest.')
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        parser.add_option("-d", "--depth", type="int", dest="depth_value",
                          help="The depth of the subdirectories to scan for AndroidManifest.xml files.")
        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            if not os.path.exists(os.path.dirname(options.log_file)):
                sys.exit("Error: Log file directory does not exist.")
            else:
                logging_file = logging.FileHandler(options.log_file, mode='a',
                                                            encoding='utf-8', delay=False)
                logging_file.setLevel(logging_level)
                logging_file.setFormatter(formatter)
                self.log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
            print("logging level: ", logging_level)
            print("verbose: ", options.verbose)
            
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
            
        if options.depth_value:
            self.DIR_DEPTH_SEARCH = options.depth_value
        # Check arguments
        if os.path.isdir(args[0]):
            self.start_main(args[0])
        else:
            sys.exit("Error: No such directory.")
    
    '''
    Get the manifest files for each apk directory.
    This uses the specified fixed depth value.
    '''
    def getManifestFiles(self, dir_name):
        depth = self.DIR_DEPTH_SEARCH
        path_separator = '*/'
        while(depth > 1):
            path_separator += path_separator
            depth -= 1
        return glob.glob(dir_name + path_separator + 'AndroidManifest.xml')
    
if __name__ == '__main__':
    ManifestFeatures().main(sys.argv[1:])  
