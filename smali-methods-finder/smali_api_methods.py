#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
import multiprocessing
from multiprocessing import Pool
from optparse import OptionParser
from subprocess import Popen, PIPE


log = logging.getLogger("smali_api_methods")
log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.

# pickled method defined at the top level of a module to be called by multiple processes.
# Runs apktool and returns the directory of the unpacked apk file.
def run_grep(apk_dir, target_dir):
    package_name = os.path.basename(apk_dir).rsplit('-', 1)[0]
    version_code = os.path.basename(apk_dir).rsplit('-', 1)[1]
    result_file_name = os.path.join(target_dir, package_name +  '-' + version_code + '.smali.txt')
    # skip the target file if it already exists
    if os.path.exists(result_file_name):
        log.info("Target file already exists")
        return
    search_word = '.invoke'
    log.info("Running grep on " + package_name)
    result_file = open(result_file_name, 'w')
    
    sub_process = Popen(
                ['grep', '-hr', search_word, apk_dir], stdout=PIPE, stderr=PIPE)
    out, err = sub_process.communicate()
    rc = sub_process.returncode
    if rc == 0:
        log.info("Writing results to %s", result_file_name)
        result_file.write(out)
    if rc != 0:
        log.error('Failed to decode apk file: ' + package_name + '\n' + err)
    result_file.close()
    return result_file_name
        
class SmaliApiMethods(object):
    # The depth of the directory listing for AndroidManifest.xml
    DIR_DEPTH_SEARCH = 1
    # Set the number of worker processes to the number of available CPUs.
    processes = multiprocessing.cpu_count()

    def __init__(self):
        self.ordered = False
    
    def start_main(self, source_dir, target_dir):
        pool = Pool(processes=self.processes)
        log.info('A pool of %i worker processes has been created', self.processes)
        count = 0
        apk_dir_list = []
        # Iterate over the unpacked apk files in the source directory.
        for apk_dir in [os.path.join(source_dir, f) for f in os.listdir(source_dir)]:
            # check if the directory is for an unpacked apk. i.e, contains
            # AndroidManifest.xml
            manifest_file = os.path.abspath(
                os.path.join(apk_dir, 'AndroidManifest.xml'))
            if os.path.isdir(apk_dir) and os.path.isfile(manifest_file):
                try:
                    package_name = os.path.basename(apk_dir).rsplit('-', 1)[0]
                    version_code = os.path.basename(apk_dir).rsplit('-', 1)[1]
                    if package_name is None or version_code is None:
                        log.error('No package name or version code found.')
                        continue
                    count += 1
                    apk_dir_list.append(apk_dir)
                    log.info("%i - Found apk dir %s", count, apk_dir)
                except IndexError:
                    log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        if len(apk_dir_list) > 0:
            try:
                # Check if files must be ordered
                if self.ordered:
                    log.info('Sorting apk files by modified date.')
                    apk_dir_list.sort(key=lambda x: os.path.getmtime(x))
                # Run apktool on the apk file asynchronously.
                print(apk_dir_list)
                results = [pool.apply_async(run_grep, (apk_dir_path, target_dir)) for apk_dir_path in apk_dir_list]
                for r in results:
                    if r is not None:
                        grep_out_file = r.get()
                        if grep_out_file is not None:
                            log.info("The output has been written at: %s", grep_out_file)
                # close the pool to prevent any more tasks from being submitted to the pool.
                pool.close()
                # Wait for the worker processes to exit
                pool.join()
            except KeyboardInterrupt:
                print('got ^C while worker processes have outstanding work. Terminating the pool and stopping the worker processes immediately without completing outstanding work..')
                pool.terminate()
                print('pool has been terminated.')
        else:
            log.error('Failed to find apk files in %s', source_dir)

        
    def main(self, args):
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
        log.addHandler(logging_console)

        # command line parser
        parser = OptionParser(
            usage="python %prog [options] unpacked_apk_dir target_dir",
            version="%prog 1.1",
            description='The smali_api_methods tool recursively searches for '
                        'invoke- methods calls and store them in one text file.')
        parser.add_option("-p", "--processes", dest="processes", type="int",
                           help="the number of worker processes to use. " +
                           "Default is the number of CPUs in the system.")
        parser.add_option('-o', '--ordered', help='Sort apk dirs by date.', dest='ordered', action='store_true', default=False)
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
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.processes:
            self.processes = options.processes
        if options.log_file:
            if not os.path.exists(os.path.dirname(options.log_file)):
                sys.exit("Error: Log file directory does not exist.")
            else:
                logging_file = logging.FileHandler(options.log_file, mode='a',
                                                   encoding='utf-8',
                                                   delay=False)
                logging_file.setLevel(logging_level)
                logging_file.setFormatter(formatter)
                log.addHandler(logging_file)
        if options.ordered:
            self.ordered = True
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
        if options.depth_value is not None:
            self.DIR_DEPTH_SEARCH = options.depth_value
        
        # Check arguments
        if os.path.isdir(args[0]) and os.path.isdir(args[1]):
            self.start_main(args[0], args[1])
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
    SmaliApiMethods().main(sys.argv[1:])
