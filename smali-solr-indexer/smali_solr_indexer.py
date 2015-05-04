#!/usr/bin/python
import sys
import os
import datetime
import logging
from optparse import OptionParser
import glob
import requests
import json


class SmaliSolrIndexer(object):
    def __init__(self):
        self.host_name = "localhost"
        self.port_number = "8983"
        self.collection_name = "sievely-code"
        self.log = logging.getLogger("smali_solr_indexer")
        self.log.setLevel(logging.DEBUG)

    def do_indexing(self, source_dir):
        smali_text_files = [os.path.abspath(p) for p in glob.glob(source_dir +
                                                                  '/*.txt')]
        solr_update_url = 'http://' + self.host_name + ':' + self.port_number + \
                          '/solr/' + self.collection_name + '/update'
        solr_extract_url = solr_update_url + '/extract'
        for text_file in smali_text_files:
            file_name = os.path.basename(text_file)
            package_name = file_name.rsplit('-', 1)[0]
            version_code = file_name.rsplit('.smali.txt')[0].rsplit('-')[1]
            app_id = package_name + "-" + version_code
            # print(int(version_code))
            solr_update_params = {"literal.id": app_id,
                                  "literal.package_name": package_name,
                                  "literal.version_code": version_code,
                                  "wt": "json"}
            myfile = {'myfile': open(text_file, 'rb')}
            r = requests.post(solr_extract_url, params=solr_update_params,
                              files=myfile)
            if r.status_code != 200:
                self.log.error("%s\nFailed to update %s-%s\nError message:%s",
                               r.url, package_name,
                               version_code, r.json())
                sys.exit(0)

            else:
                self.log.info("Successfully updated %s-%s", package_name,
                              version_code)
        # Commit all pending updates
        if len(smali_text_files) > 0:
            r = requests.post(solr_update_url,
                              headers={'content-type': 'application/json'},
                              params={"commit": 'true', "wt": "json"})
            if r.status_code == 200:
                self.log.info('Successfully committed all pending updates.')
            else:
                self.log.error("%s\nFailed to commit pending " +
                               "updates\nError message:%s", r.url, r.json())

    def is_solr_server_running(self):
        solr_admin_url = 'http://' + self.host_name + ':' + self.port_number + \
                         '/solr/admin/cores'
        r = requests.post(solr_admin_url, params={'action': 'STATUS',
                                                  'wt': 'json'})
        r_content = json.loads(r.content)
        if r.status_code == 200 and r_content['responseHeader']['status'] == 0:
            self.log.info('Apache Solr server is listening at %s:%s',
                          self.host_name, self.port_number)
            return True
        else:
            self.log.error('Solr Server Connection error \n%s', r.content)
            return False

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

        # command line parser
        parser = OptionParser(
            usage="python %prog smali_invoke_dir [options]",
            version="%prog 1.0",
            description='This tool takes a directory of text files that'
                        ' contains smali invoked methods'
                        ' and index them with Solr Cell using Apache Tika via'
                        ' HTTP POST request. Smali text files must be named as'
                        ' packageName-versionCode.smali.txt')
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        parser.add_option('-H', '--hostname', dest="host_name",
                          default="localhost", help="Solr host name")
        parser.add_option('-p', '--port', dest="port_number", default=8983,
                          type='int', help="Solr port number")
        parser.add_option('-c', '--collection', dest="collection_name",
                          default="sievely-code", help="Solr collection name")

        (options, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("incorrect number of arguments.")
        if options.host_name:
            self.host_name = options.host_name
        if options.port_number:
            self.port_number = str(options.port_number)
        if options.collection_name:
            self.collection_name = options.collection_name
        if options.log_file:
            if not os.path.exists(os.path.dirname(options.log_file)):
                sys.exit("Error: Log file directory does not exist.")
            else:
                logging_file = logging.FileHandler(options.log_file, mode='a',
                                                   encoding='utf-8',
                                                   delay=False)
                logging_file.setLevel(logging_level)
                logging_file.setFormatter(formatter)
                self.log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
        # Check arguments
        if os.path.isdir(args[0]):
            if self.is_solr_server_running():
                self.do_indexing(os.path.abspath(args[0]))
        else:
            sys.exit("Error: No such directory. %s", args[0])
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    SmaliSolrIndexer().main(sys.argv[1:])