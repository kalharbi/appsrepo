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
    cmd_desc = """\nThe following commands are available:
                       find_app_activities -p <permission_name>
                       find_all_packages_and_versions
                       find_additional_info
                       find_apps_by_target_sdk_version -s <sdk_version>
                       find_apps_by_min_sdk_version -s <sdk_version>
                       find_apps_by_max_sdk_version -s <sdk_version>
                       """
    
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
    
    def find_apps_by_target_sdk_version(self, target_sdk, target_dir):
        query = {"target_sdk_version": target_sdk}
        opts = {"package":1, "version_code":1, "target_sdk_version":1, 
                "min_sdk_version":1, "max_sdk_version":1}
        manifest_collection = self.connect_mongodb()
        cursor = manifest_collection.find(query, opts)
        if cursor.count() == 0:
            self.log.error('No documents that match the query criteria.')
            return
        result_file_name = os.path.join(os.path.abspath(target_dir),
                                    'apps_by_target_sdk_version-' + str(target_sdk) + '.csv')
        result_file = open(result_file_name, 'w')
        result_file.write('package,version_code,target_sdk,min_sdk,max_sdk' + '\n')
        for entry in cursor:
            package = entry['package'] 
            verc = entry['version_code']
            target_sdk = str(entry['target_sdk_version'])
            min_sdk = str(entry['min_sdk_version']) if 'min_sdk_version' in entry.keys() else ''
            max_sdk = str(entry['max_sdk_version']) if 'max_sdk_version' in entry.keys() else ''
            result_file.write(package + ',' + verc + ',' + target_sdk + ',' + 
                              min_sdk + ',' + max_sdk + '\n')
        result_file.close()
    
    def find_apps_by_min_sdk_version(self, min_sdk, target_dir):
        query = {"min_sdk_version": min_sdk}
        opts = {"package":1, "version_code":1, "min_sdk_version":1,
                "target_sdk_version":1, "max_sdk_version":1}
        manifest_collection = self.connect_mongodb()
        cursor = manifest_collection.find(query, opts)
        if cursor.count() == 0:
            self.log.error('No documents that match the query criteria.')
            return
        result_file_name = os.path.join(os.path.abspath(target_dir),
                                    'apps_by_min_sdk_version-' + str(min_sdk) + '.csv')
        result_file = open(result_file_name, 'w')
        result_file.write('package,version_code,min_sdk,max_sdk,target_sdk' + '\n')
        for entry in cursor:
            package = entry['package'] 
            verc = entry['version_code']
            min_sdk = str(entry['min_sdk_version'])
            max_sdk = str(entry['max_sdk_version']) if 'max_sdk_version' in entry.keys() else ''
            target_sdk = str(entry['target_sdk_version']) if 'target_sdk_version' in entry.keys() else ''
            result_file.write(package + ',' + verc + ',' + min_sdk + ',' + 
                              max_sdk + ',' + target_sdk + '\n')
        result_file.close()
    
    def find_apps_by_max_sdk_version(self, max_sdk, target_dir):
        query = {"max_sdk_version": max_sdk}
        opts = {"package":1, "version_code":1, "max_sdk_version":1,
                "target_sdk_version":1, "min_sdk_version":1}
        result_file_name = os.path.join(os.path.abspath(target_dir),
                                    'apps_by_max_sdk_version-' + str(max_sdk) + '.csv')
        manifest_collection = self.connect_mongodb()
        cursor = manifest_collection.find(query, opts)
        if cursor.count() == 0:
            self.log.error('No documents that match the query criteria.')
            return
        result_file = open(result_file_name, 'w')
        result_file.write('package,version_code,max_sdk,target_sdk,min_sdk' + '\n')    
        
        for entry in cursor:
            package = entry['package'] 
            verc = entry['version_code']
            max_sdk = str(entry['max_sdk_version'])
            target_sdk = str(entry['target_sdk_version']) if 'target_sdk_version' in entry.keys() else ''
            min_sdk = str(entry['min_sdk_version']) if 'min_sdk_version' in entry.keys() else ''
            result_file.write(package + ',' + verc + ',' + max_sdk + ',' + 
                              target_sdk + ',' + min_sdk + '\n')
        result_file.close()
    
    def find_activities(self, package_name, version_code, out_dir):
        self.log.info("package name: " + package_name + ". version code:" + version_code)
        result_file = None
        try:
            result_file_name = os.path.join(os.path.abspath(out_dir), package_name + '-' +
                                        version_code + '-activities' + '.txt')
            result_file = open(result_file_name, 'w')
        except IOError as detail:
            print(detail)
            sys.exit()
        manifest_collection = self.connect_mongodb()
        cursor = manifest_collection.find({"package": package_name,
                                  "version_code" : version_code}, {'activities' :1})
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
            self.log.error("Error: The package " + package_name + ", version code: " +
                           version_code + " doesn't exist or has no activities.")
        result_file.close()
    
    def find_all_packages_and_versions(self, out_dir):
        self.log.info("Trying to find all package names and version code values...")
        result_file = None
        try:
            result_file_name = os.path.join(os.path.abspath(out_dir), 'all_packages_nd_verions.csv')
            result_file = open(result_file_name, 'w')
        except IOError as detail:
            print(detail)
            sys.exit()
        manifest_collection = self.connect_mongodb()
        cursor = manifest_collection.find({"package": package_name,
                                  "version_code" : version_code}, 
                                  {'package': 1, 'version_code':1, 'min_sdk_version' :1})        
        if cursor.count() > 0:
            result_file.write('"package_name", "version_code", "min_sdk_version" \n')
            for entry in cursor:
                line = package_name = entry['package'] + '\n'
                try:
                    package_name = entry['package']
                    version_code = entry['version_code']
                    min_sdk_version = entry['min_sdk_version']
                    line = package_name + ',' + version_code + ',' + min_sdk_version + '\n'
                    self.log.info(line)
                    result_file.write(line)
                except KeyError:
                    continue
        else:
            self.log.error("No documents are found.")
        
        result_file.close()
    
    def find_additional_info(self, pacakge_names_file, target_dir):
        result_file = None
        try:
            result_file_name = os.path.join(os.path.abspath(target_dir), 'additional_manifest_info.csv')
            result_file = open(result_file_name, 'w')
            result_file.write('package,version_name,min_sdk,target_sdk,activities,services,libraries,meta_data,supports_screens \n')
        except IOError as detail:
            print(detail)
            sys.exit()
        
        manifest_collection = self.connect_mongodb()
        with open(pacakge_names_file, 'r') as f:
            # skip the first line since it's the header line [apk_name, download_count]
            next(f)
            for line in f:
                arr = [items.strip() for items in line.split(',')]
                package_name = arr[0]
                version_code = arr[1]
                cursor = manifest_collection.find({'package': package_name, 'version_code': version_code})        
                if cursor.count() > 0:
                    
                    for entry in cursor:
                        line = package_name = entry['package'] + '\n'
                        try:
                            package_name = entry.get('package')
                            version_name = entry.get('version_name')
                            min_sdk_version = entry.get('min_sdk_version', '')
                            target_sdk_version = entry.get('target_sdk_version', '')
                            activities = entry.get('activities', [])
                            services = entry.get('services', [])
                            uses_libraries = entry.get('uses_libraries', [])
                            meta_data = entry.get('meta_data', [])
                            supports_screens = entry.get('supports_screens', [])
                            line = package_name + ',' + version_name + ',' + min_sdk_version + ',' + target_sdk_version + ',' + str(len(activities)) + ',' + str(len(services)) + ',' + str(len(uses_libraries)) + ',' + str(len(meta_data)) + ',' + str(len(supports_screens)) + '\n'
                            self.log.info(line)
                            result_file.write(line)
                            break
                        except KeyError as e:
                            self.log.error('KeyError in %s. %s',package_name, e) 
                            continue
                else:
                    self.log.error("No documents are found for package: %s, version code: %s.", package_name, version_code)
                
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
        parser = OptionParser(usage="%prog {cmd} [OPTIONS]\n" + self.cmd_desc, version="%prog 1.0")
        parser.add_option('-p', '--package', dest="package_name",
                          help='App package name.')
        parser.add_option('-r', '--ver', dest="app_version_code",
                          help='App version code.')
        parser.add_option('-s', '--sdk-version', dest="sdk", type='int',
                          help='Android sdk version, an integer designating Android API Level number.')
        parser.add_option('-f', '--file', dest="apk_names_list_file",
                          metavar="FILE", default=0, help='read package and version code values from a file.')
        parser.add_option("-o", "--out-dir", dest="out_dir",
                          help="write output files to the given DIR. Default is the current working directory.", metavar="DIR")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
                          
        (options, args) = parser.parse_args()
        if len(args) != 1:
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
        out_dir = os.path.dirname(os.path.realpath(__file__))
        if options.out_dir:
            if not os.path.isdir(options.out_dir):
                sys.exit('Error: ' + options.out_dir + ' No such directory.')
            out_dir = os.path.abspath(options.out_dir)
        # Get apk file names
        package_names_file = None
        if options.apk_names_list_file:
            if os.path.isfile(options.apk_names_list_file):
                package_names_file = options.apk_names_list_file
            else:
                sys.exit("Error: APK names list file " + options.apk_names_list_file + " does not exist.")
        
        if args[0]:
            if(args[0] == "find_app_activities"):
                if(options.package_name and options.app_version_code):
                    self.find_activities(options.package_name, options.app_version_code, out_dir)
                else:
                    sys.exit("Error: please specify the package name and version code number."
                             "\nUsage: " + os.path.basename(__file__) +
                             " find_app_activities ~/target_dir -p <package_name> -r <version_name>")
            elif(args[0] == 'find_all_packages_and_versions'):
                self.find_all_packages_and_versions(out_dir)
            elif(args[0] == 'find_additional_info'):
                self.find_additional_info(package_names_file, out_dir)
            elif(args[0] == 'find_apps_by_target_sdk_version'):
                if options.sdk:
                    self.find_apps_by_target_sdk_version(options.sdk, out_dir)
                else:
                    sys.exit("Error: please specify the target sdk number using the -s option."
                             "\nExample usage: " + os.path.basename(__file__) +
                             " find_apps_by_target_sdk_version ./out_dir -s 18 ")
            elif(args[0] == 'find_apps_by_min_sdk_version'):
                if options.sdk:
                    self.find_apps_by_min_sdk_version(options.sdk, out_dir)
                else:
                    sys.exit("Error: please specify the minimum supported sdk number using the -s option."
                             "\nExample usage: " + os.path.basename(__file__) +
                             " find_apps_by_min_sdk_version ./out_dir -s 18 ")
            elif(args[0] == 'find_apps_by_max_sdk_version'):
                if options.sdk:
                    self.find_apps_by_max_sdk_version(options.sdk, out_dir)
                else:
                    sys.exit("Error: please specify the maximum supported sdk number using the -s option."
                             "\nExample usage: " + os.path.basename(__file__) +
                             " find_apps_by_max_sdk_version ./out_dir -s 18 ")
            else:
               sys.exit("Error: unknown command.") 
        else:
            sys.exit("Error: missing command.")
         
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    ManifestDriver().main(sys.argv[1:]) 
