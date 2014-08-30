#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
import ConfigParser
import xml.etree.ElementTree as ET
from optparse import OptionParser
from subprocess import Popen, PIPE


log = logging.getLogger("rename_apks")
log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config",     "tools.conf"))
aapt_path = config.get('tools', 'aapt')
                
def start_main(source_dir):
    apk_paths = []
    for apk_file in os.listdir(source_dir):
        if(os.path.splitext(apk_file)[1] == '.apk'):
            apk_paths.append(os.path.join(source_dir, apk_file))
    count = 0
    if len(apk_paths) > 0:
        for apk in apk_paths:
            apk_info = get_apk_info(apk)
            try:
                new_apk_name = os.path.join(os.path.dirname(apk), apk_info['name'] + '-' + apk_info['version_code'] + '.apk')
                os.rename(apk, new_apk_name)
                log.info(str(count) + "- Renamed apk file: " + apk + " to " + new_apk_name)
                count += 1
            except KeyError:
                log.error("Failed to find package name or version code for " + apk)
            except OSError:
                log.error("Failed to rename apk file: " + apk)
    else:
        log.error('Failed to find apk files in %s', source_dir)
    

# Returns a tuple containing the package, version code, and version name.
def get_apk_info(apk_path):
    sub_process = None
    out = None
    err = None
    try:
        sub_process = Popen([aapt_path, 'dump', 'badging', apk_path], stdout=PIPE, stderr=PIPE)
        out, err = sub_process.communicate()
    except OSError:
        print('Error: aapt tool is not defined in the config file at: ./config/tools.conf')
        sys.exit(-1)
    version_info = {}
    if out:
        for line in out.split('\n'):
            segment = line.strip().split(":")
            if(segment is not None and len(segment) > 0):
                if(segment[0] == "package"):
                    package_info = segment[1].strip().split(' ')
                    for info_line in package_info:
                        info = info_line.strip().split('=')
                        if(info[0] == "name"):
                            version_info['name'] = info[1].replace("'", "")
                        elif(info[0] == 'versionCode'):
                            version_info['version_code'] = info[1].replace("'", "")
                        elif(info[0] == 'versionName'):
                            version_info['version_name'] = info [1].replace("'", "")
                    break
    # Return a hash of version code and version name
    return version_info
    
        
def main(args):
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
    log.addHandler(logging_console)
        
    # command line parser
    parser = OptionParser(usage="python %prog apk_files_directory [options]", version="%prog 1.0")
    parser.add_option("-l", "--log", dest="log_file",
                      help="write logs to FILE.", metavar="FILE")
    parser.add_option('-v', '--verbose', dest="verbose", default=0,
                      action='count', help='increase verbosity.')
                          
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments.")
    if options.log_file:
        logging_file = logging.FileHandler(options.log_file, mode='a',
                                           encoding='utf-8', delay=False)
        logging_file.setLevel(logging_level)
        logging_file.setFormatter(formatter)
        log.addHandler(logging_file)
    if options.verbose:
        levels = [logging.ERROR, logging.INFO, logging.DEBUG]
        logging_level = levels[min(len(levels) - 1, options.verbose)]
            
        # set the file logger level if it exists
        if logging_file:
            logging_file.setLevel(logging_level)
    # Check target directory
    source_dir = None
    if os.path.isdir(args[0]):
        source_dir = os.path.abspath(args[0])
    else:
        sys.exit("Error: source directory " + args[0] + " does not exist.")
    
    start_main(source_dir)
     
    print("======================================================")
    print("Finished after " + str(datetime.datetime.now() - start_time))
    print("======================================================")
    

if __name__ == '__main__':
    main(sys.argv[1:])
