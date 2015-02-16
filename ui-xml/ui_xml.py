#!/usr/bin/python
import os.path
import datetime
import logging
import sys
import yaml
from optparse import OptionParser
from helpers.resources_listing import ResourcesListing
from layout_parser import LayoutParser
from lxml import etree
from xml.etree import ElementTree

class UIXML(object):
    
    def __init__(self):
        self.log = logging.getLogger("ui_xml")
        self.log.setLevel(logging.DEBUG)
        
    def parse_file(self, layout_file):
        self.log.info('parsing %s', layout_file)
    
    def write_xml_file(self, xml_file, root):
        with open(xml_file, 'w+') as f:
            f.write(etree.tostring(root, pretty_print=True))
            f.close()
    
    def start_main(self, source_dir):
        count = 1
        # Iterate over the unpacked apk files in the source directory.
        for apk_dir in [os.path.join(source_dir, d) for d in 
                        os.listdir(source_dir)]:
            self.log.info('Parsing %s', apk_dir)
            package_name = None
            version_name = None
            version_code = None
            if not os.path.exists(os.path.join(apk_dir, 'AndroidManifest.xml')):
                self.log.error('AndroidManifest.xml is missing in %s . ' + 
                          'Unable to find package and version info.', apk_dir)
                continue
            version_name, version_code, package_name = self.get_app_info_from_manifest(
                         os.path.join(apk_dir, 'AndroidManifest.xml'))
            if not package_name:
                self.log.error('Failed to find package name for %s', apk_dir)
                continue
            if not version_code or not version_name:
                apktool_yml = os.path.join(apk_dir, 'apktool.yml')
                if not os.path.exists(apktool_yml):
                    self.log.error('Failed to find apktool.yml file for %s',
                                  apk_dir)
                    continue
                version_code, version_name = self.get_app_versions_from_yaml(
                                                                 apktool_yml)
                if not version_code or not version_name:
                    self.log.error('Failed to find app version for %s', apk_dir)
                    continue
            ui_xml_dir = os.path.abspath(os.path.join(apk_dir, 'ui-xml'))
            if not os.path.exists(ui_xml_dir):
                os.makedirs(ui_xml_dir)
            ui_xml_file = os.path.join(ui_xml_dir, package_name + '-' +
                          version_code + '.xml')
            root = etree.Element('App')
            root.set('name', package_name)
            root.set('version_code', version_code)
            # If the UI xml file exists, delete it and create a new one.
            if(os.path.exists(ui_xml_file)):
                os.remove(ui_xml_file)
            # check if the directory is for an unpacked apk. i.e, contains
            # res/ sub directory.
            if not os.path.exists(os.path.abspath(
                os.path.join(apk_dir, 'res'))):
                self.log.error('no res directory in %s', apk_dir)
                continue
            layout_dirs = ResourcesListing.get_all_layout_dirs(apk_dir)
            self.log.info("%i - APK %s has %i layout directories", count, 
                          apk_dir, len(layout_dirs))
            count += 1
            for layout_dir in layout_dirs:
                dir_element = etree.Element('Directory')
                dir_element.set('directory_name', os.path.basename(layout_dir))
                root.append(dir_element)
                layout_files = ResourcesListing.get_all_layout_files(layout_dir)
                for layout_file in layout_files:
                    file_element = etree.Element('File')
                    file_element.set('file_name', os.path.basename(layout_file))
                    dir_element.append(file_element)
                    layout_tree = LayoutParser().parse(layout_file, apk_dir)
                    if layout_tree is not None:
                        file_element.append(layout_tree.getroot())
            self.write_xml_file(ui_xml_file, root)
            self.log.info('UI XML has been written to %s' %(ui_xml_file))
        
        
    def get_app_info_from_manifest(self, manifest_file):
        tree = etree.parse(manifest_file)
        root = tree.getroot()
        package_name = root.get('package')
        version_code = root.get('versionCode')
        version_name = root.get('versionName')
        return version_name, version_code, package_name
    
    def get_app_versions_from_yaml(self, yaml_file):
        # Read apktool.yaml to get the version code and name values
        try:
            self.log.info("Processing file %s.", yaml_file)
            if not os.path.isfile(yaml_file):
                self.log.error("YAML file does not exist %s", yaml_file)
                return None
            doc = None
            with open(yaml_file, 'r') as f:
                doc = yaml.load(f)
            version_code = doc.get('versionInfo', None).get('versionCode', None)
            version_name = doc.get('versionInfo', None).get(
                'versionName', None)
            return version_code, version_name
        except yaml.YAMLError as exc:
            self.log.error("Error in apktool yaml file:", exc)
        except AttributeError as exc:
            self.log.error("sdk versions info is missing", exc)
            
    def get_version_name_from_strings_xml(self, strings_xml_file, 
                                          attribute_name):
        tree = ET.parse(strings_xml_file)
        root = tree.getroot()
        for element in root.findall('string'):
            if(element.get('name') == attribute_name):
                return element.text
    
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
        self.log.addHandler(logging_console)

        usage_info = "python %prog <root_unpacked_apk_directories> [options]"
        
        description_paragraph = ("DESCRIPTION: A tool for parsing Android xml"
            " layout files and storing them in one XML file to simplify"
            " UI analysis. It resolves resource references"
            " (e.g., @string/cancel_btn) and embeded layouts (e.g., using the"
            " <include/> and <merge/>" " tags). The final xml file is saved"
            " inside the unpacked apk directory under a sub-directory named ui-xml.")
        
        # command line parser
        parser = OptionParser(
            usage=usage_info, description = description_paragraph,
            version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option("-v", "--verbose", dest="verbose", default=0,
                          action="count", help="increase verbosity.")
        
        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            logging_file = logging.FileHandler(options.log_file, mode='a',
                                               encoding='utf-8', delay=False)
            logging_file.setLevel(logging_level)
            logging_file.setFormatter(formatter)
            self.log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
                
        # Check if directory exists
        if os.path.isdir(args[0]):
            source_dir = os.path.abspath(args[0])
        else:
            sys.exit("Error: source directory " + args[0] + " does not exist.")
            
        self.start_main(args[0])

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
    
if __name__ == '__main__':
    UIXML().main(sys.argv[1:])