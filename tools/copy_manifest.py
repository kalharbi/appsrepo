#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import yaml
from optparse import OptionParser
from lxml import etree
from lxml.etree import XMLSyntaxError


class CopyManifest(object):
    """
    Recursively searches for manifest files and copies them into a directory
    using the following naming scheme packageName-versionCode.
    """
    log = logging.getLogger("apkFinder_log")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)

    android_namespace = "http://schemas.android.com/apk/res/android"
    nsmap = {'android': android_namespace}

    def do_copy(self, source_directory, target_dir):
        for apk_dir in os.listdir(source_directory):
            manifest = os.path.join(source_directory, apk_dir,
                                    'AndroidManifest.xml')
            if os.path.exists(manifest):
                root, package_name, version_code = self.parse_manifest(manifest)
                if root is None:
                    self.log.error("Failed to parse AndroidManifest file %s",
                                   manifest)
                    continue
                if package_name is None:
                    self.log.error("Package name is missing in %s", manifest)
                    continue
                if version_code is None:
                    self.log.error("Version code is missing in %s", manifest)
                    continue
                target_manifest_file_name = os.path.join(target_dir,
                                                         package_name + '-' +
                                                         version_code + '.xml')
                with open(target_manifest_file_name, 'w+') as target_manifest:
                    target_manifest.write(
                        etree.tostring(root, pretty_print=True))
                self.log.info("Manifest file has been saved at: %s",
                              target_manifest_file_name)
            else:
                self.log.warning('Manifest file does not exist ', manifest)


    @staticmethod
    def get_info_from_apktoolyml(apktoolyml_file):
        with open(apktoolyml_file, 'r') as f:
            data = yaml.load(f)
            target_sdk = min_sdk = max_sdk = version_name = version_code = None
            sdk_info = data.get('sdkInfo', None)
            version_info = data.get('versionInfo', None)
            if sdk_info is not None:
                target_sdk = sdk_info.get('targetSdkVersion', None)
                min_sdk = sdk_info.get('minSdkVersion', None)
                max_sdk = sdk_info.get('maxSdkVersion', None)
            if version_info is not None:
                version_code = version_info.get('versionCode', None)
                version_name = version_info.get('versionName', None)
            return (target_sdk, min_sdk, max_sdk), (version_name, version_code)

    def parse_manifest(self, manifest_file):
        self.log.info('Parsing Manifest file %s', manifest_file)
        package_name = version_info = sdk_info = None
        root = None
        try:
            tree = etree.parse(manifest_file)
            root = tree.getroot()
            package_name = root.attrib['package']
            version_code = root.attrib['versionCode']
            version_name = root.attrib['versionName']
            version_info = (version_name, version_code)
        except KeyError:
            pass
        except XMLSyntaxError:
            return None, None, None
        apktool_yml = os.path.join(os.path.abspath(manifest_file + '/../'),
                      'apktool.yml')
        if os.path.exists(apktool_yml):
            sdk_info, version_info_yml = self.get_info_from_apktoolyml(
                apktool_yml)
            if version_info_yml is not None and (v is not None for v in
                                                 version_info_yml):
                version_info = version_info_yml

        if version_info is not None and version_info[0] is not None:
            root.attrib['versionName'] = version_info[0]
        if version_info is not None and version_info[1] is not None:
            root.attrib['versionCode'] = version_info[1]
        # If sdk info is found in apktool.yml file
        if sdk_info and all(v is None for v in sdk_info) is False:
            if root.find('uses-sdk') is None:
                sdk_elem = etree.Element("uses-sdk")
                root.append(sdk_elem)
            sdk_elem = root.find('uses-sdk')
            if sdk_elem is not None and sdk_info[0]:
                sdk_elem.attrib[
                    '{' + self.nsmap['android'] + '}' + 'targetSdkVersion'] = \
                    sdk_info[0]
            if sdk_elem is not None and sdk_info[1]:
                sdk_elem.attrib[
                    '{' + self.nsmap['android'] + '}' + 'minSdkVersion'] = \
                    sdk_info[1]
            if sdk_elem is not None and sdk_info[2]:
                sdk_elem.attrib[
                    '{' + self.nsmap['android'] + '}' + 'maxSdkVersion'] = \
                    sdk_info[2]
        version_code = None
        if version_info is not None and version_info[1] is not None:
            version_code = version_info[1]

        return root, package_name, version_code

    def main(self, args):
        start_time = datetime.datetime.now()
        # Configure logging
        logging_level = logging.ERROR
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s' +
                                      ' - %(message)s')
        # Create console logger and set its formatter and level
        logging_console = logging.StreamHandler(sys.stdout)
        logging_console.setFormatter(formatter)
        logging_console.setLevel(logging.DEBUG)
        # Add the console logger
        self.log.addHandler(logging_console)

        # command line parser
        parser = OptionParser(usage="%prog [options] search_directory " \
                                    "target_manifest_files_dir",
                              description="%prog -- Recursively search for AndroidManifest.xml files in" \
                                          "search_directory and copy them to target_manifest_files_dir ",
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
        if not os.path.isdir(args[0]):
            sys.exit("Error: search directory " + args[0] +
                     " does not exist.")
        if not os.path.isdir(args[1]):
            sys.exit("Error: target manifest files directory " + args[1] +
                     " does not exist.")

        self.do_copy(args[0], args[1])
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    CopyManifest().main(sys.argv[1:])
