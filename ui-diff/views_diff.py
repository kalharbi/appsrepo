#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import json
from optparse import OptionParser

class ViewsDiff(object):
    
    log = logging.getLogger("ViewsExtractor")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
    
    def find_in_old(self, view_to_find, old_views):
        for view in old_views:
            if str(view) == str(view_to_find):
                return True
        return False
    
    def compute_diff(self, old_file, new_file, out_dir):
        # Extract the package and version code from the file named in
        # the following naming scheme:
        # views-package-version_code.json
        new_file_name = os.path.basename(new_file)
        old_file_name = os.path.basename(old_file)
        package_name_new = new_file_name[new_file_name.index("-") + 1 : new_file_name.rindex("-")]
        version_code_new = new_file_name[new_file_name.rindex("-") + 1 : new_file_name.rindex(".json")]
        package_name_old = old_file_name[old_file_name.index("-") + 1 : old_file_name.rindex("-")]
        version_code_old = old_file_name[old_file_name.rindex("-") + 1 : old_file_name.rindex(".json")]
        result_file_name = os.path.join(os.path.abspath(out_dir),
                                        'views-diff-' + package_name_new + "-" + 
                                        version_code_new + "-diff-" + version_code_old + ".json")
        self.log.info("Comparing the views of %s-%s with %s-%s", 
                      package_name_new, version_code_new, 
                      package_name_old, version_code_old)
        json_file = open(result_file_name, 'w')
        added_views_list = []
        
        new_json = json.loads(open(new_file).read())
        new_views = new_json['views']
        old_json = json.loads(open(old_file).read())
        old_views = old_json['views']
        
        for view in new_views:
            if not self.find_in_old(view, old_views):
                added_views_list.append(view)
        
        views_json = {"package_new": package_name_new, "version_code_new" : version_code_new,
                      "package_old": package_name_old, "version_code_old" : version_code_old,
                      "views_added" : added_views_list}
        json.dump(views_json, json_file, sort_keys= True, indent=4)
        
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
        parser = OptionParser(usage = "python %prog <old_views_file> <new_views_file> [OPTIONS]\n", version = "%prog 1.0")
        parser.add_option("-l", "--log", dest = "log_file",
                          help = "write logs to FILE.", metavar = "FILE")
        parser.add_option("-o", "--out-dir", dest = "out_dir",
                          help = "write output files to the given DIR. Default is the current working directory.",
                          metavar = "DIR")
        (options, args) = parser.parse_args()
        out_dir = os.path.dirname(os.path.realpath(__file__))
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.out_dir:
            if not os.path.isdir(options.out_dir):
                sys.exit('Error: ' + options.out_dir + ' No such directory.')
            out_dir = os.path.abspath(options.out_dir)
        if options.log_file:
            if os.path.exists(options.log_file):
                sys.exit("Error: Log file already exists.")
            else:
                logging_file = logging.FileHandler(options.log_file, mode = "a",
                                                            encoding = "utf-8",
                                                            delay = False)
                logging_file.setLevel(logging_level)
                logging_file.setFormatter(formatter)
                self.log.addHandler(logging_file)
        out_dir = os.path.dirname(os.path.realpath(__file__))
        if options.out_dir:
            if not os.path.isdir(options.out_dir):
                sys.exit('Error: ' + options.out_dir + ' No such directory.')
            out_dir = os.path.abspath(options.out_dir)
        old_views_file = args[0]
        if not os.path.isfile(old_views_file):
            sys.exit("Error: old_views_file " + old_views_file + " does not exist.")
        new_views_file = args[1]
        if not os.path.isfile(new_views_file):
            sys.exit("Error: new_views_file doesn't exist. " + new_views_file)
        self.compute_diff(old_views_file, new_views_file, out_dir)
        self.log.info("The results have been saved at %s", out_dir)
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
        
if __name__ == '__main__':
    ViewsDiff().main(sys.argv[1:])