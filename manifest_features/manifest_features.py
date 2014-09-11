# !/usr/bin/python
import sys
import os.path
import json
import glob
import datetime
import logging
import logging.handlers
import xml.etree.ElementTree as ET
from optparse import OptionParser

from pymongo.errors import ConnectionFailure, InvalidName

import yaml
from pymongo import MongoClient

from manifest_parser import ManifestParser
from custom_json_encoder import CustomJsonEncoder


class ManifestFeatures(object):
    """This script parses AndroidManifest.xml files and stores them in MongoDB.
    """

    DB_NAME = "apps"
    COLLECTION_NAME = "manifest"
    PORT_NUMBER = 27017
    HOST_NAME = "localhost"
    # The depth of the directory listing for AndroidManifest.xml
    DIR_DEPTH_SEARCH = 1
    log = logging.getLogger("manifest_features")
    log.setLevel(
        logging.DEBUG)  # The logger's level must be set to the "lowest" level.

    def connect_mongodb(self):
        try:
            client = MongoClient(self.HOST_NAME, self.PORT_NUMBER)
            db = client[self.DB_NAME]
            manifest_collection = db[self.COLLECTION_NAME]
            self.log.info("Connected to database: %s Collection: %s.",
                          self.DB_NAME,
                          self.COLLECTION_NAME)
            return manifest_collection
        except ConnectionFailure:
            sys.exit("ERROR: Connection to the database failed or is lost.")
        except InvalidName:
            sys.exit("ERROR: Invalid database name")

    @staticmethod
    def document_exists(manifest_collection, app_manifest):
        return manifest_collection.find_one(
            {"package": app_manifest.package, "version_code":
                app_manifest.version_code})

    def start_main(self, dir_name):
        manifest_collection = self.connect_mongodb()
        manifest_files = self.get_manifest_files(dir_name)
        for manifest_file in manifest_files:
            self.log.info("Processing file: %s.", manifest_file)
            app_manifest = ManifestParser().parse(manifest_file)
            if app_manifest is None:
                self.log.error('Failed to parse AndroidManifest file: %s', manifest_file)
                continue
            
            # set min,max, target sdk version values
            if app_manifest.min_sdk_version is None or app_manifest.max_sdk_version is None or app_manifest.target_sdk_version is None:
                apktool_yaml_file = os.path.join(os.path.dirname(manifest_file),
                                                 'apktool.yml')
                app_sdk_versions = self.get_app_sdk_versions(apktool_yaml_file)
                if app_sdk_versions is None:
                    self.log.warning('No sdk versions found in ' + apktool_yaml_file)
                else:
                    if app_sdk_versions[0]:
                        app_manifest.set_uses_min_sdk(app_sdk_versions[0])
                    if app_sdk_versions[1]:
                        app_manifest.set_uses_max_sdk(app_sdk_versions[1])
                    if app_sdk_versions[2]:
                        app_manifest.set_uses_target_sdk(app_sdk_versions[2])
            # set version values
            if app_manifest.version_name is None or app_manifest.version_code is None:
                app_versions = self.get_app_versions(apktool_yaml_file)
                if app_versions is None:
                    self.log.error('%s is not found.',apktool_yaml_file)
                    continue
                app_manifest.version_code = app_versions[0]
                app_manifest.version_name = app_versions[1]
            
            if app_manifest.version_name.startswith('@string/'):
                strings_xml_file = os.path.join(os.path.dirname(manifest_file), 'res', 'values', 'strings.xml')
                if not os.path.isfile(strings_xml_file):
                    self.log.error("strings.xml file does not exist %s", strings_xml_file)
                    continue
                
                attribute_name = app_manifest.version_name.split('/')[1]
                attribute_value = self.get_version_name_from_strings_xml(strings_xml_file, attribute_name)
                if attribute_value is not None:
                    app_manifest.version_name = attribute_value.strip()
            
            if app_manifest.version_code.startswith('@string/'):
                strings_xml_file = os.path.join(os.path.dirname(manifest_file), 'res', 'values', 'strings.xml')
                if not os.path.isfile(strings_xml_file):
                    self.log.error("strings.xml file does not exist %s", strings_xml_file)
                    continue
                
                attribute_name = app_manifest.version_code.split('/')[1]
                attribute_value = self.get_version_name_from_strings_xml(strings_xml_file, attribute_name)
                if attribute_value is not None:
                    app_manifest.version_code = attribute_value.strip()
                
            if self.document_exists(manifest_collection, app_manifest):
                self.log.info("Already Exists.")
                continue
            else:
                json_manifest = json.dumps(app_manifest, indent=2,
                                           cls=CustomJsonEncoder)
                manifest_collection.insert(json.loads(json_manifest))
                self.log.info(
                    "Inserted a new document for apk: %s; version:%s",
                    app_manifest.package, app_manifest.version_name)
        if len(manifest_files) == 0:
            self.log.error(
                "Error: Failed to find AndroidManifest.xml files in %s" +
                " in the depth of %d directories.\nTry to change the depth" +
                " value using the command line option -d",
                dir_name, self.DIR_DEPTH_SEARCH)

    def get_app_sdk_versions(self, yaml_file):
        # Read apktool.yaml to get the min, max, and target sdk versions
        try:
            self.log.info("Processing file %s.", yaml_file)
            if not os.path.isfile(yaml_file):
                self.log.error("YAML file does not exist %s", yaml_file)
                return None
            doc = None
            with open(yaml_file, 'r') as f:
                doc = yaml.load(f)
            min_sdk_version = doc.get('sdkInfo', None).get('minSdkVersion',
                                                           None)
            max_sdk_version = doc.get('sdkInfo', None).get('maxSdkVersion',
                                                           None)
            target_sdk_version = doc.get('sdkInfo', None).get(
                'targetSdkVersion', None)
            if min_sdk_version is not None:
                min_sdk_version = int(min_sdk_version)
            if max_sdk_version is not None:
                max_sdk_version = int(max_sdk_version)
            if target_sdk_version is not None:
                target_sdk_version = int(target_sdk_version)
            return min_sdk_version, max_sdk_version, target_sdk_version
        except yaml.YAMLError as exc:
            self.log.error("Error in apktool yaml file:", exc)
        except AttributeError as exc:
            self.log.error("sdk versions info is missing", exc)
    
    def get_app_versions(self, yaml_file):
        # Read apktool.yaml to get the version code and name values
        try:
            self.log.info("Processing file %s.", yaml_file)
            if not os.path.isfile(yaml_file):
                self.log.error("YAML file does not exist %s", yaml_file)
                return None
            doc = None
            with open(yaml_file, 'r') as f:
                doc = yaml.load(f)
            version_code = doc.get('versionInfo', None).get('versionCode',
                                                           None)
            version_name = doc.get('versionInfo', None).get(
                'versionName', None)
            return version_code, version_name
        except yaml.YAMLError as exc:
            self.log.error("Error in apktool yaml file:", exc)
        except AttributeError as exc:
            self.log.error("sdk versions info is missing", exc)
        
        
    def get_version_name_from_strings_xml(self, strings_xml_file, attribute_name):
        tree = ET.parse(strings_xml_file)
        root = tree.getroot()
        for element in root.findall('string'):
            if(element.get('name') == attribute_name):
                return element.text
        
    def main(self):
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
        parser = OptionParser(
            usage="python %prog [options] apk_dir ",
            version="%prog 1.1",
            description='The manifest_features tool recursively searches for '
                        'a directory of unpacked apk files, parses their '
                        'AndroidManifest.xml files and stores them in a '
                        'MongoDB collection named manifest.')
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        parser.add_option(
            "-d",
            "--depth",
            type="int",
            dest="depth_value",
            help="The depth of the subdirectories to scan for "
                 "AndroidManifest.xml files.")
        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            if not os.path.exists(os.path.dirname(options.log_file)):
                sys.exit("Error: Log file directory does not exist.")
            else:
                logging_file = logging.FileHandler(options.log_file, mode='a',
                                                   encoding='utf-8',
                                                   delay=False)
                logging_file.setLevel(logging_level)
                logging_file.setFormatter(formatter)
                self.log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
        if options.depth_value is not None:
            self.DIR_DEPTH_SEARCH = options.depth_value
        
        # Check arguments
        if os.path.isdir(args[0]):
            self.start_main(args[0])
        else:
            sys.exit("Error: No such directory.")

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


    def get_manifest_files(self, dir_name):
        '''
        Get the manifest files for each apk directory.
        This uses the specified fixed depth value.
        '''
        depth = self.DIR_DEPTH_SEARCH
        path_separator = '*/'
        if depth < 1:
            path_separator = ''
        while depth > 1:
            path_separator += path_separator
            depth -= 1
        return glob.glob(dir_name + path_separator + 'AndroidManifest.xml')


if __name__ == '__main__':
    ManifestFeatures().main()
