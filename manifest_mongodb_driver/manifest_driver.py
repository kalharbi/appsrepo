#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import json
from optparse import OptionParser
from pymongo import MongoClient

class ManifestDriver(object):
    
    DB_NAME = "apps"
    COLLECTION_NAME = "manifest"
    PORT_NUMBER = 27017
    HOST_NAME = "localhost"
    log = logging.getLogger("manifest_driver")
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
    
    def find_activities(self, package_name, version_name, out_dir):
        self.log.info("package name: " + package_name + ". version:" + version_name)
        result_file = None
        try:
            result_file_name = os.path.join(os.path.abspath(out_dir), package_name + '-' +
                                        version_name + '-activities' + '.txt')
            result_file = open(result_file_name, 'w')
        except IOError as detail:
            print(detail)
            sys.exit()
        manifest_collection = self.connect_mongodb()
        cursor = manifest_collection.find({"package": package_name,
                                  "version_name" : version_name}, {'activities' :1})
        if cursor.count() > 0:
            for entry in cursor:
                activities = entry['activities']
                for activity in activities:
                    activity_name = activity['activity']['name']
                    # Find main activity
                    try:
                        if activity['intentFilter']:
                            for action in activity['intentFilter']['action']:
                                if action['name'] == 'android.intent.action.MAIN':
                                    activity_name ='[Main] ' + activity_name
                    except KeyError:
                        continue
                    finally:
                        self.log.info(activity_name)
                        result_file.write(activity_name + '\n')
        else:
            self.log.error("Error: The package " + package_name + ", version: " +
                           version_name + " doesn't exist or has no activities.")
        result_file.close()
    
    def main(self, argv):
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
        parser = OptionParser(usage="%prog [options] {find_app_activities} out_dir ", version="%prog 1.0")
        parser.add_option('-p', '--package', dest="package_name",
                          help='App package name.')
        parser.add_option('-r', '--ver', dest="app_version",
                          help='App version name.')
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
                          
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            if os.path.exists(options.log_file):
                sys.exit("Error: Log file already exists.")
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
        
        # Check target directory
        out_dir = None
        if os.path.isdir(args[1]):
            out_dir = args[1]
        else:
            sys.exit("Error: target directory " + args[1] + " does not exist.")
        
        if args[0]:
            if(args[0] == "find_app_activities"):
                if(options.package_name and options.app_version):
                    self.find_activities(options.package_name, options.app_version, out_dir)
                else:
                    sys.exit("Error: please specify the package name and version number."
                             "\nUsage: " + os.path.basename(__file__) +
                             " find_app_activities ~/target_dir -p <package_name> -r <version_name>")
            else:
               sys.exit("Error: unknown command.") 
        else:
            sys.exit("Error: missing command.")
         
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    ManifestDriver().main(sys.argv[1:]) 