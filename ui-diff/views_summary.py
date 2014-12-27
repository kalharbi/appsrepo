#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import json
from optparse import OptionParser

class ViewsSummary(object):
    
    log = logging.getLogger("ViewsSummary")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
    
    def create_summary(self, views_diff_file, out_dir):
        base_name = os.path.basename(views_diff_file)
        result_file_name = 'summary-' + os.path.splitext(base_name)[0] + ".csv"
        csv_file = open(result_file_name, 'w')
        json_data = json.loads(open(views_diff_file).read())
        views = json_data['views_added']
        csv_file.write('name,text,src,style\n')
        for v in views:
            src = ''
            name = ''
            text = ''
            style = ''
            if 'name' in v.keys():
                name = v['name']
            if 'android:src' in v.keys():
                src = v['android:src']
            if 'android:text' in v.keys():
                text = v['android:text']
            if 'style' in v.keys():
                style = v['style']
            csv_file.write(name + "," + '"' + text + '"' + "," + '"' + src + '"' + ","  '"' + style + '"\n')
        self.log.info('The summary of the views diff file %s has been written at %s', views_diff_file, result_file_name)
        csv_file.close()
        
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
        parser = OptionParser(usage = "python %prog <views_diff_file> [OPTIONS]\n", version = "%prog 1.0")
        parser.add_option("-l", "--log", dest = "log_file",
                          help = "write logs to FILE.", metavar = "FILE")
        parser.add_option("-o", "--out-dir", dest = "out_dir",
                          help = "write output files to the given DIR. Default is the current working directory.",
                          metavar = "DIR")
        (options, args) = parser.parse_args()
        out_dir = os.path.dirname(os.path.realpath(__file__))
        if len(args) != 1:
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
        views_diff_file = args[0]
        if not os.path.isfile(views_diff_file):
            sys.exit("Error: views_diff_file doesn't exist. " + views_diff_file)
        self.create_summary(views_diff_file, out_dir)
        self.log.info("The results have been saved at %s", out_dir)
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
        
if __name__ == '__main__':
    ViewsSummary().main(sys.argv[1:])