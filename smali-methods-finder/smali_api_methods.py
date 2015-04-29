#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
import multiprocessing
import yaml
from multiprocessing import Pool
from optparse import OptionParser
from subprocess import Popen, PIPE
from lxml import etree
from lxml.etree import XMLSyntaxError

log = logging.getLogger("smali_invoked_methods")
log.setLevel(
    logging.DEBUG)  # The logger's level must be set to the "lowest" level.

# pickled method defined at the top level of a module to be called by
# multiple processes.
# Runs apktool and returns the directory of the unpacked apk file.
def run_grep(smali_dir, target_file):
    # skip the target file if it already exists
    if os.path.exists(target_file):
        log.info("Target file already exists")
        return
    search_word = '.invoke'
    log.info("Running grep on " + smali_dir)
    result_file = open(target_file, 'w')

    sub_process = Popen(
        ['grep', '-hr', search_word, smali_dir], stdout=PIPE, stderr=PIPE)
    out, err = sub_process.communicate()
    rc = sub_process.returncode
    if rc == 0:
        log.info("Writing results to %s", target_file)
        result_file.write(out)
    if rc != 0:
        log.error('Failed to run grep on : ' + smali_dir + '\n' + err)
    result_file.close()
    return target_file


class SmaliApiMethods(object):
    def __init__(self):
        # The depth of the directory listing for AndroidManifest.xml
        self.dir_depth_search = 1
        # Set the number of worker processes to the number of available CPUs.
        self.processes = multiprocessing.cpu_count()

    def get_manifest_files(self, dir_name):
        '''
        Get the manifest files for each apk directory.
        This uses the specified fixed depth value.
        '''
        depth = self.dir_depth_search
        path_separator = '*/'
        if depth < 1:
            path_separator = ''
        while depth > 1:
            path_separator += path_separator
            depth -= 1
        return glob.glob(dir_name + path_separator + 'AndroidManifest.xml')

    @staticmethod
    def get_app_info_from_manifest(manifest_file):
        version_name = version_code = package_name = None
        try:
            tree = etree.parse(manifest_file)
            root = tree.getroot()
            package_name = root.get('package')
            version_code = root.get('versionCode')
            version_name = root.get('versionName')
        except XMLSyntaxError:
            log.error('Invalid XML in the AndroidManifest file %s',
                      manifest_file)
        return version_name, version_code, package_name

    @staticmethod
    def get_app_versions_from_yaml(yaml_file):
        # Parse apktool.yaml to get the version code and name values
        version_code = version_name = None
        try:
            log.info("Processing file %s.", yaml_file)
            if not os.path.isfile(yaml_file):
                log.error("YAML file does not exist %s", yaml_file)
                return None
            doc = None
            with open(yaml_file, 'r') as f:
                doc = yaml.load(f)
            version_code = doc.get('versionInfo', None).get('versionCode', None)
            version_name = doc.get('versionInfo', None).get(
                'versionName', None)
        except yaml.YAMLError:
            log.error("Error in apktool yaml file: %s", yaml_file)
        except AttributeError:
            log.error("sdk versions info is missing in yaml file: %s",
                      yaml_file)
        return version_code, version_name

    def start_main(self, source_dir, target_dir):
        pool = Pool(processes=self.processes)
        log.info('A pool of %i worker processes has been created',
                 self.processes)
        results = []
        manifest_files = self.get_manifest_files(source_dir)
        for manifest_file in manifest_files:
            # check if the directory is for an unpacked apk. i.e., contains
            # AndroidManifest.xml
            apk_dir = os.path.abspath(os.path.join(manifest_file, '../'))
            log.info('Searching in %s', apk_dir)
            version_name, version_code, package_name = \
                self.get_app_info_from_manifest(manifest_file)
            if not package_name:
                log.error('Failed to find package name for %s', apk_dir)
                continue
            if not version_code or not version_name:
                apktool_yml = os.path.join(apk_dir, 'apktool.yml')
                if not os.path.exists(apktool_yml):
                    log.error('Failed to find apktool.yml file for %s',
                              apk_dir)
                    continue
                version_code, version_name = self.get_app_versions_from_yaml(
                    apktool_yml)
                if not version_code or not version_name:
                    log.error('Failed to find app version for %s', apk_dir)
                    continue
            result_file_name = os.path.join(target_dir, package_name + '-' +
                                            version_code + '.smali.txt')
            # do not overwrite existing smali method invocation text files
            if os.path.exists(result_file_name):
                log.warning('Smali text file already exists %s',
                            result_file_name)
                continue
            smali_root_dir = os.path.join(apk_dir, 'smali',
                                          package_name.split('.')[0])
            if not os.path.exists(smali_root_dir):
                log.error('No smali directory found at %s', apk_dir)
                continue
            results.append(pool.apply_async(run_grep,
                                            [smali_root_dir, result_file_name]))
        try:
            # Run grep on the smali root directories asynchronously.
            for r in results:
                if r is not None:
                    grep_out_file = r.get()
                    if grep_out_file is not None:
                        log.info("The output has been written at: %s",
                                 grep_out_file)
            # close the pool to prevent any further tasks from
            # being submitted to the pool.
            pool.close()
            # Wait for the worker processes to exit
            pool.join()
        except KeyboardInterrupt:
            print(
                'got ^C while worker processes have outstanding work. ' +
                'Terminating the pool and stopping the worker processes' +
                ' immediately without completing outstanding work..')
            pool.terminate()
            print('pool has been terminated.')

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
            usage="python %prog unpacked_apk_dir target_dir [options]",
            version="%prog 1.1",
            description='This tool recursively searches for '
                        'invoke- methods calls and store them in one text file.')
        parser.add_option("-p", "--processes", dest="processes", type="int",
                          help="the number of worker processes to use. " +
                               "Default is the number of CPU cores.")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        parser.add_option("-d", "--depth", type="int", dest="depth_value",
                          help="The depth of the child directories to scan " +
                               "for AndroidManifest.xml files. Default is: " +
                               str(self.dir_depth_search))
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
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
        if options.depth_value:
            self.dir_depth_search = options.depth_value

        # Check arguments
        if os.path.isdir(args[0]) and os.path.isdir(args[1]):
            self.start_main(args[0], args[1])
        else:
            sys.exit("Error: No such directory.")

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    SmaliApiMethods().main(sys.argv[1:])
