#!/usr/bin/python
import sys
import os.path
import datetime
import ConfigParser
import tempfile
import shutil
from subprocess import Popen, PIPE
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "config.conf"))

host_name = config.get('db', 'host')
port_number = config.getint('db', 'port')
db_name = config.get('db', 'db')
collection_name = config.get('db', 'collection')
path_field_name = config.get('db', 'path_field_name')
done_field_name = config.get('db', 'done_field_name')

apktool_executor = config.get('tools', 'apktool_executor')
ui_xml_extractor = config.get('tools', 'ui_xml_extractor')
manifest_extractor = config.get('tools', 'manifest_extractor')
api_calls_extractor = config.get('tools', 'api_calls_extractor')

apktool_out = config.get('out', 'apktool_out')
listing_out = config.get('out', 'listing_out')
ui_xml_out = config.get('out', 'ui_xml_out')
manifest_out = config.get('out', 'manifest_out')
code_out = config.get('out', 'code_out')

apktool_log = config.get('logs', 'apktool_log')
ui_xml_log = config.get('logs', 'ui_xml_log')
manifest_log = config.get('logs', 'manifest_log')
code_log = config.get('logs', 'code_log')

if not os.path.exists(apktool_out):
    try:
        os.mkdir(apktool_out)
    except OSError:
        print("Failed to create " + apktool_out)
        sys.exit(1)

def ensure_config_exists(config_name, config_value):
    if not os.path.exists(config_value):
        print("Error: in config: " + config_name +
              "=" + config_value +
              " path does not exist.")
        sys.exit(1)


# Ensure that the path values in the config file do exist.
for section in ['tools', 'out']:
    for name, value in config.items(section):
        ensure_config_exists(name, value)

for name, value in config.items('logs'):
    ensure_config_exists(name, os.path.dirname(value))


def connect_mongodb():
    try:
        client = MongoClient(host_name, port_number)
        db = client[db_name]
        apk_files_collection = db[collection_name]
        print('Connected to ' + host_name + ':' + str(port_number) +
              ', database: ' + db_name +
              ' Collection:' + collection_name)
        return apk_files_collection
    except ConnectionFailure:
        print('Error: Connection failed to ' + host_name + ':' +
              str(port_number) + ', database: ' + db_name +
              ' Collection:' + collection_name)
        sys.exit(1)
    except InvalidName:
        sys.exit("ERROR: Invalid database name")


def write_new_apk_paths(out_file, apk_path_collection):
    """ Write un extracted apk files to a tmp file. """
    f = open(out_file, 'w')
    for doc in apk_path_collection.find({done_field_name: False}):
        f.write(doc[path_field_name] + os.linesep)
    for doc in apk_path_collection.find({done_field_name:
                                        {"$exists": False}}):
        f.write(doc[path_field_name] + os.linesep)
    f.close()


def run_processes(args):
    print(args)
    try:
        sub_process = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = sub_process.communicate()
        rc = sub_process.returncode
        if rc == 0:
            print(out)
        else:
            print("Failed to execute " + err)
    except OSError as e:
        print("OSError({0}): {1}".format(e.errno, e.strerror))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def copy_listing_details_files(apk_paths_file, target_dir):
    with open(apk_paths_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '.apk' not in line:
                continue
            apk_dir_path = os.path.dirname(line)
            listing_dir_path = os.path.dirname(apk_dir_path)
            id = os.path.basename(line).split('.apk')[0]
            listing_json_file = os.path.join(listing_dir_path,
                                             id + '.listing.json')
            reviews_json_file = os.path.join(listing_dir_path,
                                             'GooglePlay-' + id + '.json5')
            # copy listing details and review files
            if os.path.exists(listing_json_file):
                copy_file(listing_json_file, target_dir)
            if os.path.exists(reviews_json_file):
                copy_file(reviews_json_file, target_dir)


def copy_file(source, destination):
    try:
        shutil.copy(source, destination)
    except IOError:
        print("Failed to copy file " + source)


def update_apk_paths_collection(apk_path_collection, apk_paths_file):
    with open(apk_paths_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '.apk' not in line:
                continue
            package_name, version_code = os.path.basename(line).split('.apk')[0].split('-')
            apk_path_collection.find_one_and_update(
                {'n': package_name, 'verc': version_code},
                {'$set': {done_field_name: True}})


def start_task():
    start_time = datetime.datetime.now()
    apk_paths_collection = connect_mongodb()
    _, file_path = tempfile.mkstemp(text=True, suffix='.txt')
    write_new_apk_paths(file_path, apk_paths_collection)
    if os.stat(file_path).st_size == 0:
        print('No new APK files are found.')
        sys.exit(0)
    # Run apktool executor
    run_processes(['python', apktool_executor, file_path,
                   apktool_out, '-l', apktool_log])
    # Run ui-xml
    run_processes(['python', ui_xml_extractor, apktool_out, '-o',
                  ui_xml_out, '-l', ui_xml_log])
    # Run manifest
    run_processes(['python', manifest_extractor, apktool_out,
                  manifest_out, '-l', manifest_log])
    # Run API calls
    run_processes(['python', api_calls_extractor, apktool_out,
                  code_out, '-l', code_log])
    # Run listing details and reviews
    copy_listing_details_files(file_path, listing_out)
    # Mark the apps as done
    update_apk_paths_collection(apk_paths_collection, file_path)
    # Delete unpacked APK files
    shutil.rmtree(apktool_out, ignore_errors=True)
    print("All apks have been extracted " + file_path)
    print("======================================================")
    print("Finished after " + str(datetime.datetime.now() - start_time))
    print("======================================================")


if __name__ == '__main__':
    start_task()
