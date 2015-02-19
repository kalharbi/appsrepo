#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
import multiprocessing
from multiprocessing import Pool
import xml.etree.ElementTree as ET
from optparse import OptionParser
from subprocess import Popen, PIPE
import ConfigParser


log = logging.getLogger("apktool_executor")
log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "tools.conf"))
aapt_path = config.get('tools', 'aapt')

# pickled method defined at the top level of a module to be called by multiple processes.
# Runs apktool and returns the directory of the unpacked apk file.
def run_apktool(apk_file, target_dir, framework_dir, tag, no_src, no_res):
    print("Running apktool on " + apk_file)
    apk_name = os.path.basename(os.path.splitext(apk_file)[0])
    target_dir = os.path.join(target_dir, apk_name)
    apk_version_info = get_apk_info(apk_file)
    # skip the target directory if it already exists
    if os.path.exists(target_dir):
        log.info("Target directory already exists")
        return
        
    args = ['apktool', 'd', apk_file, '-o', target_dir]
    if framework_dir:
        args.append('-p')
        args.append(framework_dir)
    elif tag:
        args.append('-t')
        args.append(tag)
    elif no_src:
        args.append('-s')
    elif no_res:
        args.append('-r')
    sub_process = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = sub_process.communicate()
    rc = sub_process.returncode
    if rc == 0:
        log.info(out)
    if rc != 0:
        log.error('Failed to decode apk file: ' + apk_file + '\n' + err)
    return target_dir, apk_version_info

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
        
class ApktoolExecutor(object):
    # Set the number of worker processes to the number of available CPUs.
    processes = multiprocessing.cpu_count()
    # Flag that indicates the use of custom directory naming scheme. 
    #      Example: dir/c/com/a/amazon/com.amazon

    def __init__(self):
        self.apk_files = []
        self.framework_dir = None
        self.tag = None
        self.no_src = False
        self.no_res = False
        self.ordered = False
        self.use_custom_file_search = False
        self.path_file = None
        self.apk_names_list_file = None
    
            
    def start_main(self, source_dir, target_dir):
        apk_paths = []
        # Create pool of worker processes
        pool = Pool(processes=self.processes)
        log.info('A pool of %i worker processes has been created', self.processes)
        # if the package names file is given
        if self.apk_names_list_file:
            with open(self.apk_names_list_file, 'r') as f:
                # skip the first line since it's the header 
                # line [apk_name, download_count]
                next(f)
                for line in f:
                    arr = [items.strip() for items in line.split(',')]
                    apk_name = arr[0]
                    apk_path = source_dir
                    if apk_name:
                        if self.use_custom_file_search:
                            # Use custom directory search to limit the search
                            # to the directories of each apk file.
                            for index, item in enumerate(apk_name.split('.')):
                                apk_path = os.path.join(apk_path, item[0], item)
                                if index == 1:
                                    break
                        apk_paths.append(self.find_apk_file(apk_name, apk_path))
        
        
        # If the apk path file is given
        elif self.path_file:
            with open(self.path_file, 'r') as f:
                for line in f:
                    apk_paths.append(line)
        # If apk path file or package list file are not given, 
        # run apktool on each apk file in the source directory.
        else:
            for apk_file in os.listdir(source_dir):
                if(os.path.splitext(apk_file)[1] == '.apk'):
                    apk_paths.append(os.path.join(source_dir, apk_file))

        if len(apk_paths) > 0:
            try:
                # Check if files must be ordered
                if self.ordered:
                    log.info('Sorting apk files by modified date.')
                    apk_paths.sort(key=lambda x: os.path.getmtime(x))
                # Run apktool on the apk file asynchronously.
                results = [pool.apply_async(run_apktool, (apk_path, target_dir,
                                                          self.framework_dir, self.tag,
                                                          self.no_src, self.no_res))
                                                          for apk_path in apk_paths]
                for r in results:
                    if(r != None):
                        target_dir, apk_version_info = r.get()
                        apktool_file = os.path.join(target_dir, 'apktool.yml')
                        if not os.path.exists(apktool_file):
                            self.write_version_to_apktoolyml(apktool_file, 
                                                             apk_version_info)
                        log.info("APK file has been extracted at: " + target_dir)
                # close the pool to prevent any more tasks from being 
                # submitted to the pool.
                pool.close()
                # Wait for the worker processes to exit
                pool.join()
            except KeyboardInterrupt:
                print('got ^C while worker processes have outstanding work. '
                'Terminating the pool and stopping the worker processes'
                ' immediately without completing outstanding work..')
                pool.terminate()
                print('pool has been terminated.')
        else:
            log.error('Failed to find apk files in %s', source_dir)
                        
    def write_version_to_apktoolyml(self, apktool_file, version_info):
        with open(apktool_file, 'w') as f:
            f.write('versionInfo:\n')
            f.write("  versionCode: '" + version_info['version_code']+ "'\n")
            f.write("  versionName: " + version_info['version_name']+ "\n")
    
    def find_apk_file(self, apk_name, source_directory):
        if(not os.path.exists(source_directory)):
            log.error(source_directory + ' No such file or directory.')
            return None
        
        self.files_listing(os.path.abspath(source_directory), apk_name,'.apk')
        found_apk_files = self.apk_files
        self.apk_files = []
        if len(found_apk_files) == 1:
            log.info('Found APK file:' + found_apk_files[0])
            return found_apk_files[0]
        elif len(found_apk_files) > 1:
            log.warning('Found ' + str(len(found_apk_files))  + ' files for apk ' + apk_name + '. ' +
                             ', '.join([str(x) for x in found_apk_files]))
            return found_apk_files[0]
        elif len(found_apk_files) == 0:
            log.error('Could not find the apk file for ' + apk_name + ' in: '+ 
                            source_directory)
        return None
    
    def files_listing(self, source, apk_name, ext_name):
        for item in os.listdir(source):
            file = os.path.join(source, item)
            log.info('searching for ' + apk_name + ' in ' + file)
            if(os.path.isdir(file)):
                self.files_listing(file, apk_name, ext_name)
            elif(os.path.splitext(file)[1].lower() == ext_name and 
                 apk_name.startswith(os.path.basename(os.path.splitext(file)[0]))):
                    self.apk_files.append(file)
    
    @staticmethod
    # check apktool version.
    def check_apktool_version():
        sub_process = Popen(['apktool', '--version'], 
                            stdout=PIPE, stderr=PIPE)
        out, err = sub_process.communicate()
        if out:
            # Only accept version 2.0 or higher
            if int(out.strip().split('.')[0]) == 2:
                print('using apktool version ' + out.strip())
            else:
                raise Exception('Unsatisfied dependencies for apktool. ' + 
                                'Please install apktool version 2.0.0-Beta9 or higher. ' + 
                                'See the README file for additional information.')
        
    def main(self, args):
        # check apktool version
        self.check_apktool_version()
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
        parser = OptionParser(usage="python %prog apk_source_directory "
                             "target_directory [options]", version="%prog 1.0")
        parser.add_option("-p", "--processes", dest="processes", type="int",
                           help="the number of worker processes to use. " +
                           "Default is the number of CPUs in the system.")
        parser.add_option("-w", "--framework", help="forces apktool to use "
                          "framework files located in <FRAMEWORK_DIR>."
                          , dest="framework_dir")
        parser.add_option("-t", "--tag", help="forces apktool to use framework"
                          " files tagged by <TAG>.", dest="tag")
        parser.add_option("-s", "--no-src", help="Do not decode sources.", 
                          dest="no_src", action='store_true', default=False)
        parser.add_option("-r", "--no-res", help="Do not decode resources.", 
                          dest="no_res", action='store_true', default=False)
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='increase verbosity.')
        parser.add_option('-f', '--file', dest="apk_names_list_file",
                          metavar="FILE", help='read apk names from a file '
                          'that contains a list of APK names.')
        parser.add_option('-i','--path-file', dest= 'path_file',
                          metavar='FILE', help= 'read apk path names from a '
                          'file')
        parser.add_option('-o', '--ordered', help='Sort apk files by date.', 
                          dest='ordered', action='store_true', default=False)
        parser.add_option('-c', '--custom', dest= "custom_search", 
                          action= 'store_true', default=False,
                          help="search for apk files using the custom "
                          "directory naming scheme;"
                          " e.g., dir/c/com/a/amazon/com.amazon")
                          
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.processes:
            self.processes = options.processes
        if options.framework_dir:
            self.framework_dir = options.framework_dir
        if options.tag:
            self.tag = options.tag
        if options.no_src:
            self.no_src = True
        if options.no_res:
            self.no_res = True
        if options.ordered:
            self.ordered = True
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
        if options.custom_search:
            self.use_custom_file_search = True
        if options.path_file:
            self.path_file = option.path_file
        # Get apk file names
        if options.apk_names_list_file:
            if os.path.isfile(options.apk_names_list_file):
                self.apk_names_list_file = options.apk_names_list_file
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
    
        self.start_main(source_dir, target_dir)
     
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
    

if __name__ == '__main__':
    ApktoolExecutor().main(sys.argv[1:])
