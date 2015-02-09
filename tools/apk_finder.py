#!/usr/bin/python
import sys
import os.path
import datetime
import logging
from optparse import OptionParser

class APKFinder(object):
    """
    Recursively search for apk files and write their absoulte paths to a file.
    """
    log = logging.getLogger("apkFinder_log")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.

    def files_listing(self, source_directory, ext_name, out_file):
        for item in os.listdir(source_directory):
            file = os.path.join(source_directory, item)
            if (os.path.isdir(file)):
                self.log.info('searching for apk files in ' + file)
                self.files_listing(file, ext_name, out_file)
            elif (os.path.splitext(file)[1].lower() == ext_name):
                self.log.info('Found apk file %s', file)
                out_file.write(os.path.abspath(file) + '\n')
    
    def start_main(self, search_directory, target_apk_paths_file):
        out_file = open(target_apk_paths_file, 'w')
        self.files_listing(os.path.abspath(search_directory), '.apk', out_file)
        self.log.info('APK paths have been saved at %s', os.path.abspath(target_apk_paths_file))
        out_file.close()
        
    
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
        parser = OptionParser(usage="%prog [options] search_directory target_apk_paths_file",
                              description= '%prog -- Recursively search for apk files in search_directory ' +
                              'and write their absoulte paths to a file (target_apk_paths_file).',
                              version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            logging_file = logging.FileHandler(options.log_file, mode='a',
                                               encoding='utf-8', delay=False)
            logging_file.setLevel(logging_level)
            logging_file.setFormatter(formatter)
            self.log.addHandler(logging_file)
        if os.path.isdir(args[0]):
            destination_dir = os.path.abspath(args[0])
        else:
            sys.exit("Error: local source directory " + args[0] + " does not exist.")
        if os.path.isfile(args[1]) or os.path.isdir(args[1]):
            sys.exit('Error: target_apk_paths_file already exists')
        
        self.start_main(args[0], args[1])
            
        
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
        
if __name__ == '__main__':
    APKFinder().main(sys.argv[1:]) 