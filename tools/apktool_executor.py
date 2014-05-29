#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
import xml.etree.ElementTree as ET
from optparse import OptionParser
from subprocess import Popen, PIPE

class ApktoolExecutor(object):
    
    apktool_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                'bin', 'apktool1.5.2', 'apktool.jar')
    log = logging.getLogger("apktool_executor")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
    # Flag that indicates the use of custom directory naming scheme. i.e. dir/c/com/a/amazon/com.amazon
    use_custom_file_search = False
    
    def __init__(self):
        self.apk_files = []
    
    def run_apktool(self, apk_file, target_dir):
        self.log.info("Running apktool on " + apk_file)
        apk_name = os.path.basename(os.path.splitext(apk_file)[0])
        target_dir = os.path.join(target_dir, apk_name)
        sub_process = Popen(['java', '-jar', self.apktool_path, 'd', apk_file, target_dir], 
                            stdout=PIPE, stderr=PIPE)
        out, err = sub_process.communicate()
        if out:
            self.log.info(out)
        if err:
            self.log.error(err)
        return target_dir
            
    def start_main(self, apk_names_file, source_dir, target_dir):
        # If apk list file is not given, run apktool on each apk file in the source directory.
        if not apk_names_file:
            for apk_file in os.listdir(source_dir):
                if(os.path.splitext(apk_file)[1] == '.apk'):
                    result_dir = self.run_apktool(os.path.join(source_dir, apk_file), target_dir)
                    # Rename the unpacked apk directory.
                    apk_info = self.get_apk_info(result_dir)
                    new_name = os.path.join(os.path.dirname(result_dir),
                                            apk_info[0] + '-' + apk_info[1])
                    os.rename(result_dir, new_name)
                    self.log.info("APK file has been extracted at: " + new_name)
            return
            
        with open(apk_names_file, 'r') as f:
            # skip the first line since it's the header line [apk_name, download_count]
            next(f)
            for line in f:
                arr = [items.strip() for items in line.split(',')]
                apk_name = arr[0]
                apk_path = source_dir
                if apk_name:
                    if self.use_custom_file_search:
                        # Use custom directory search to limit the search to the directories of each apk file.
                        for index, item in enumerate(apk_name.split('.')):
                            apk_path = os.path.join(apk_path, item[0], item)
                            if index == 1:
                                break
                    apk_file = self.find_apk_file(apk_name, apk_path)
                    if apk_file:
                        # Run apktool on the first file in the list
                        # TODO: Handle multiple versions files.
                        result_dir = self.run_apktool(apk_file, target_dir)
                        # Rename the unpacked apk directory.
                        apk_info = self.get_apk_info(result_dir)
                        new_name = os.path.join(os.path.dirname(result_dir),
                                                apk_info[0] + '-' + apk_info[1])
                        os.rename(result_dir, new_name)
                        self.log.info("APK file has been extracted at: " + new_name)
                        
                
    def find_apk_file(self, apk_name, source_directory):
        if(not os.path.exists(source_directory)):
            self.log.error(source_directory + ' No such file or directory.')
            return None
        
        self.files_listing(os.path.abspath(source_directory), apk_name,'.apk')
        found_apk_files = self.apk_files
        self.apk_files = []
        if len(found_apk_files) == 1:
            self.log.info('Found APK file:' + found_apk_files[0])
            return found_apk_files[0]
        elif len(found_apk_files) > 1:
            self.log.warning('Found ' + str(len(found_apk_files))  + ' files for apk ' + apk_name + '. ' +
                             ', '.join([str(x) for x in found_apk_files]))
            return found_apk_files[0]
        elif len(found_apk_files) == 0:
            self.log.error('Could not find the apk file for ' + apk_name + ' in: '+ 
                            source_directory)
        return None
    
    def files_listing(self, source, apk_name, ext_name):
        for item in os.listdir(source):
            file = os.path.join(source, item)
            self.log.info('searching for ' + apk_name + ' in ' + file)
            if(os.path.isdir(file)):
                self.files_listing(file, apk_name, ext_name)
            elif(os.path.splitext(file)[1].lower() == ext_name and 
                 apk_name.startswith(os.path.basename(os.path.splitext(file)[0]))):
                    self.apk_files.append(file)
    
    def get_apk_info(self, apk_dir):
        """Return a tuple containing the package and version names."""
        manifest_file = os.path.join(apk_dir, 'AndroidManifest.xml')
        tree = ET.parse(manifest_file)
        root = tree.getroot()
        version_code = None
        version_name = None
        package_name = None
        for name, value in root.attrib.items():
            if(name == 'package'):
                package_name = value
            elif(name.endswith('versionCode')):
                version_code = value
            elif(name.endswith('versionName')):
                version_name = value
        if version_name:
            return (package_name, version_name)
        else:
            return (package_name, version_code)
        
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
        parser = OptionParser(usage="%prog apk_source_directory target_directory [options]", version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='increase verbosity.')
        parser.add_option('-f', '--file', dest="apk_names_list_file",
                          metavar="FILE", default=0, help='read apk names from a file that contains a list of APK names.')
        parser.add_option('-c', '--custom', dest="custom_search", action='store_true', default=False,
                          help="search for apk files using the custom directory naming scheme. e.g, dir/c/com/a/amazon/com.amazon")
                          
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
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
        if options.custom_search:
            self.use_custom_file_search = True
        # Get apk file names
        apk_names_file = None
        if options.apk_names_list_file:
            if os.path.isfile(options.apk_names_list_file):
                apk_names_file = options.apk_names_list_file
            else:
                sys.exit("Error: APK names list file " + options.apk_names_list_file + " does not exist.")
        # Check target directory
        source_dir = None
        target_dir = None
        if os.path.isdir(args[0]):
            source_dir = os.path.abspath(args[0])
        else:
            sys.exit("Error: source directory " + args[0] + " does not exist.")
    
        if os.path.isdir(args[1]):
            target_dir = os.path.abspath(args[1])
        else:
            sys.exit("Error: target directory " + args[1] + " does not exist.")
    
        self.start_main(apk_names_file, source_dir, target_dir)
     
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
    

if __name__ == '__main__':
    ApktoolExecutor().main(sys.argv[1:])
