#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import glob
import shutil
from optparse import OptionParser

class FindNdCopy(object):
    
    log = logging.getLogger("find_nd_copy")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
    
    def __init__(self):
        self.apk_files = []
        
    def start_main(self, apk_names_file, source_dir, target_dir):
        with open(apk_names_file, 'r') as f:
            # skip the first line since it's the header line [apk_name, download_count]
            next(f)
            for line in f:
                arr = [items.strip() for items in line.split(',')]
                apk_name = arr[0]
                apk_path = source_dir
                if apk_name:
                    # Only search in the directory of each apk file.
                    for index, item in enumerate(apk_name.split('.')):
                        apk_path = os.path.join(apk_path, item[0])
                        apk_path = os.path.join(apk_path, item)
                        if index == 1:
                            break
                    apk_path = os.path.join(apk_path, apk_name)
                    apk_files = self.find_apk_file(apk_name, apk_path)
                    if apk_files:
                        # Copy the first file in the list
                        # TODO: Handle multiple versions files.
                        self.copy_file(apk_files[0], target_dir)
                
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
            return found_apk_files
        elif len(found_apk_files) == 0:
            self.log.error('Could not find the apk file for ' + apk_name + ' in: '+ 
                            source_directory)
        return None
          
    def copy_file(self, apk_file, target_directory):
        self.log.info("copying file " + apk_file + ' to ' + target_directory)
        try:
            shutil.copy(apk_file, target_directory)
        except IOError as e:
            self.log.error(str(e))
          
    def files_listing(self, source, apk_name, ext_name):
        for item in os.listdir(source):
            file = os.path.join(source, item)
            self.log.info('searching for ' + apk_name + ' in ' + file)
            if(os.path.isdir(file)):
                self.files_listing(file, apk_name, ext_name)
            elif(os.path.splitext(file)[1].lower() == ext_name and os.path.basename(os.path.splitext(file)[0]).startswith(apk_name)):
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
        parser = OptionParser(usage="%prog [options] apk_names_file source_directory target_directory", version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
                          
        (options, args) = parser.parse_args()
        if len(args) != 3:
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
            
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
        
        # Get apk file names
        apk_names_file = None
        if os.path.isfile(args[0]):
            apk_names_file = args[0]
        else:
            sys.exit("Error: APK names list file " + args[0] + " does not exist.")
        # Check target directory
        source_dir = None
        target_dir = None
        if os.path.isdir(args[1]):
            source_dir = os.path.abspath(args[1])
        else:
            sys.exit("Error: source directory " + args[1] + " does not exist.")
        
        if os.path.isdir(args[2]):
            target_dir = os.path.abspath(args[2])
        else:
            sys.exit("Error: target directory " + args[2] + " does not exist.")
        
        self.start_main(apk_names_file, source_dir, target_dir)
         
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
        

if __name__ == '__main__':
    FindNdCopy().main(sys.argv[1:]) 