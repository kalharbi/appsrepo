#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import glob
import shutil
import getpass
import paramiko
import base64
import ConfigParser
import multiprocessing
import errno
from multiprocessing import Pool, Value, Lock
from subprocess import Popen, PIPE
from optparse import OptionParser
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName


log = logging.getLogger("apk_downloader")
log.setLevel(
    logging.DEBUG)  # The logger's level must be set to the "lowest" level.
MAX_APK_PER_DIR = 100
dir_counter = None
files_counter = None
counter = 0
target_directory = None
counter_lock = None


def get_immediate_subdirectories(dir_path):
    return [os.path.join(dir_path, name) for name in os.listdir(dir_path)
            if os.path.isdir(os.path.join(dir_path, name))]


def get_destination_dir():
    with counter_lock:
        global dir_counter
        global files_counter
        if files_counter.value < MAX_APK_PER_DIR:
            files_counter.value += 1
        else:
            files_counter.value = 0
            dir_counter.value += 1
        directory = os.path.join(target_directory, str(dir_counter.value))
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
        return directory


def init_destination_dir(dir_c, files_c):
    ''' store the counter for later use '''
    global dir_counter
    global files_counter
    global counter_lock
    counter_lock = Lock()
    with counter_lock:
        dir_counter = dir_c
        files_counter = files_c
        sub_dirs_full_path = get_immediate_subdirectories(target_directory)
        sub_dirs = [int(os.path.basename(x)) for x in sub_dirs_full_path]
        sub_dirs.sort()
        for d in sub_dirs:
            dir_path = os.path.join(target_directory, str(d))
            files = [f for f in os.listdir(dir_path) if
                     os.path.isfile(os.path.join(dir_path, f))]
            if len(files) < MAX_APK_PER_DIR:
                dir_counter.value = d
                files_counter.value = len(files)
                break


# pickled method defined at the top level of a module to be called by multiple processes.
# Runs async and returns the path of the downloaded file.
def run_async(apk_dict, remote_pw, remote_user_name, remote_host_name):
    app_info = apk_dict['info']
    apk_path = apk_dict['apk_file']
    custom_file_name = app_info["package_name"] + '-' + app_info[
        "version_code"] + '.apk'
    destination_dir = get_destination_dir()
    destination_apk_file = os.path.join(destination_dir, custom_file_name)
    apk_file = apk_path.strip()
    log.info("Downloading APK file %s", apk_file)
    # Run rsync to download the remote apk file
    command = "sshpass -p " + remote_pw + " rsync " + remote_user_name + \
          "@" + remote_host_name + ":" + apk_file + " " + \
          destination_apk_file
    sub_process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = sub_process.communicate()
    rc = sub_process.returncode
    if rc != 0:
        log.error('Failed to download apk file: ' + apk_file + '\n' + err)
        return None, None
    return destination_apk_file, app_info


class ApkDownloader(object):
    """
     Download apk files from a remote server into a local server.
     The local server contains directories named in numeric numbers,
     and each directory contains only 100 APK files.
     Example: target_dir/1 # contins 100 APK files
              target_dir/2 # contins 100 APK files
              target_dir/3 # contins 100 APK files
              
    """

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "config", "tools.conf"))
    # Set the number of worker processes to the number of available CPUs.
    processes = multiprocessing.cpu_count()

    def __init__(self):
        self.apk_files = []
        self.host_name = "localhost"
        self.port_number = 27017
        self.db_name = 'apps'
        self.collection_name = 'apks'
        self.remote_pw = ''
        self.remote_host_name = ''
        self.remote_user_name = ''
        self.ssh_client = None

    def connect_to_ssh(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.remote_host_name,
                                username=self.remote_user_name,
                                password=self.remote_pw)

    def connect_mongodb(self):
        try:
            client = MongoClient(self.host_name, self.port_number)
            db = client[self.db_name]
            apk_files_collection = db[self.collection_name]
            log.info("Connected to %s:%s, database: %s, Collection: %s.",
                     self.host_name, self.port_number, self.db_name,
                     self.collection_name)
            return apk_files_collection
        except ConnectionFailure:
            print("Connected to {host}:{port}, database: {db}" +
                  " Collection: {collection}. failed or is lost.".format(
                      host=self.host_name, port=self.port_number,
                      db=self.db_name, collection=self.collection_name))
            sys.exit(1)
        except InvalidName:
            sys.exit("ERROR: Invalid database name")

    @staticmethod
    def document_exists(apk_collection, package_name, version_code):
        """ Check if the file exists in this apk_bukcet collection. """
        if (apk_collection.find(
                {"metadata.n": package_name,
                 "metadata.verc": version_code}).count() > 0):
            return True
        else:
            return False

    def get_app_info(self, apk_file):
        """ Returns package name, version code, and version name by 
        running aapt on the apk file.
        """
        log.info('Running aapt to find version information for %s', apk_file)
        version_info = {}
        aapt_path = self.config.get('tools', 'aapt')
        stdin, stdout, stderr = self.ssh_client.exec_command(aapt_path +
                        ' dump badging ' + apk_file)
        if stdout.channel.recv_exit_status() != 0:
            log.error("Failed to run aapt on %s. %s", apk_file,
                      str(''.join(stderr.readlines())))
            return None
        else:
            for line in stdout.read().splitlines():
                segment = line.strip().split(':')
                if (segment is not None and len(segment) > 1):
                    if (segment[0] == "package"):
                        package_info = segment[1].strip().split(' ')
                        for info_line in package_info:
                            info = info_line.strip().split('=')
                            if (info[0] == "name"):
                                version_info['package_name'] = info[1].replace(
                                    "'", "")
                            elif (info[0] == "versionCode"):
                                # Remove the ' character from the string value
                                version_info['version_code'] = info[1].replace(
                                    "'", "")
                            elif (info[0] == "versionName"):
                                version_info['version_name'] = info[1].replace(
                                    "'", "")
                        break
        return version_info


    def get_file_size(self, file):
        statinfo = os.stat(file)
        return statinfo.st_size

    def start_main(self, remote_apk_paths_file):
        files_counter = Value('i', 0)
        dir_counter = Value('i', 0)
        # Create pool of worker processes
        pool = Pool(initializer=init_destination_dir, processes=self.processes,
                    initargs=(files_counter, dir_counter, ))
        log.info('A pool of %i worker processes has been created',
                 self.processes)
        # Connect to MongoDB
        apks_collection = self.connect_mongodb()
        apks_dicts = []
        with open(remote_apk_paths_file, 'r') as apk_list_file:
            for apk_file in apk_list_file:
                app_info = self.get_app_info(apk_file)
                if app_info is None:
                    log.error('Failed to find version info for APK file %s',
                                   apk_file)
                    continue
                additional_metadata = {"n": app_info["package_name"],
                                       "verc": app_info["version_code"],
                                       "vern": app_info["version_name"]}
                if (
                self.document_exists(apks_collection, app_info["package_name"],
                                     app_info["version_code"])):
                    log.info(
                        "APK file for package %s, version code: %s already exists.",
                        app_info["package_name"], app_info["version_code"])
                    continue
                else:
                    apks_dicts.append({'apk_file': apk_file, 'info': app_info})
        if len(apks_dicts) > 0:
            # Run apktool on the apk file asynchronously.
            results = [pool.apply_async(run_async, (apk_dict,
                                                    self.remote_pw,
                                                    self.remote_user_name,
                                                    self.remote_host_name))
                       for apk_dict in apks_dicts]
            for r in results:
                if (r != None):
                    destination_apk_file, app_info = r.get()
                    if (destination_apk_file is None or app_info is None):
                        continue
                    log.info("APK file %s-%s has been downloaded at: %s",
                             app_info["package_name"],
                             app_info["version_code"], destination_apk_file)
                    # insert the path to mongodb collection
                    apk_file_doc = {'n': app_info["package_name"],
                                    'verc': app_info["version_code"],
                                    'vern': app_info["version_name"],
                                    'size': self.get_file_size(
                                        destination_apk_file),
                                    'path': os.path.abspath(
                                        destination_apk_file)}
                    doc_id = apks_collection.insert(apk_file_doc)
                    log.info(
                        "A new document (Id: %s) containing metadata for  %s." +
                        "has been inserted in collection: %s",
                        doc_id, destination_apk_file, self.collection_name)
            # close the pool to prevent any more tasks from being submitted to the pool.
            pool.close()
            # Wait for the worker processes to exit
            pool.join()

        else:
            log.error('Failed to find apk files in %s', remote_apk_paths_file)


    def main(self, args):
        global target_directory
        global log
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
            usage="%prog [options] remote_apk_paths_file local_destination_directory",
            version="%prog 1.0",
            description='%prog -- Download a list of apk files from a remote ' +
                        ' server into a local server.' +
                        '-- Arguments: <remote_apk_paths_file>: a text file ' +
                        'that contains the full path names to the apk files ' +
                        'at the remote server.' +
                        ' <local_destination_directory>: a directory at the ' +
                        'local server at which the apk files are downloaded.')
        parser.add_option('-H', '--host', dest='host_name',
                          help='The host name that the mongod is connected to.' +
                          'Default value is localhost.',
                          default='localhost')
        parser.add_option('-p', '--port', dest='port_number', type='int',
                          default=27017,
                          help='The port number that the mongod instance is ' +
                          'listening. Default is 27017.')
        parser.add_option('-b', '--db', dest='db_name',
                          help='The name of MongoDB database to store the apk' +
                          ' paths. Default is apps.')
        parser.add_option('-c', '--collection', dest='collection_name',
                          help='The name of the MongoDB collection to store ' +
                          'the paths. Default is apks.')
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        parser.add_option("-s", "--processes", dest="processes", type="int",
                          help="the number of worker processes to use. " +
                               "Default is the number of CPUs in the system.")
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.processes:
            self.processes = options.processes
        if options.host_name:
            self.host_name = options.host_name
        if options.port_number:
            self.port_number = options.port_number
        if options.db_name:
            self.db_name = options.db_name
        if options.collection_name:
            self.collection_name = options.collection_name
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

        # Check local destination directory
        if os.path.isdir(args[1]):
            target_directory = os.path.abspath(args[1])
        else:
            sys.exit("Error: local destination directory " + args[
                1] + " does not exist.")
        if not os.path.isfile(args[0]):
            sys.exit(
                "Error: remote apk paths file " + args[0] + " does not exist.")

        print(
            'This tool will establish an ssh connection to the remote server.')
        print(
            'Remote server connection information is required to issue rsync commands:')
        self.remote_host_name = raw_input('Enter the remote server name: ')
        self.remote_user_name = raw_input('Enter the user name for the remote server: ')
        self.remote_pw = getpass.getpass('Enter the password for the remote server: ')
        try:
            self.connect_to_ssh()
            self.start_main(args[0])
        finally:
            if self.ssh_client:
                # close the ssh client
                log.info('Closing the ssh client..')
                self.ssh_client.close()
                log.info('The ssh client has been closed')

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


def ensure_shell_command_is_installed(command):
    import subprocess
    return_code = subprocess.call(command, shell=True)
    if return_code !=0:
        sys.exit('Error: The shell command "' + command + '" is not installed on ' +
                 'the local server')

if __name__ == '__main__':
    ensure_shell_command_is_installed("sshpass")
    ApkDownloader().main(sys.argv[1:]) 
