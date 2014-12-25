#!/usr/bin/python
import sys
import os.path
import datetime
import logging
import json
from py2neo import Graph
from py2neo.error import GraphError
from optparse import OptionParser

class ViewsExtractor(object):
    
    port = 7474
    host = "localhost"
    db_path = None
    log = logging.getLogger("ViewsExtractor")
    log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.
    
    def __connect_neo4j(self):
        graph = None
        try:
            '''
            # TODO: py2neo has problem when changing default port of the local server.
            address = "http://" + self.host + ":" + str(self.port) + self.db_path
            graph = Graph(address)
            '''
            # Use the default port 7474 just for now
            graph = Graph()
        except GraphError:
            sys.exit
        return graph
        
    def find_views(self, apk_names_list_file, out_dir):
        graph = self.__connect_neo4j()
        if graph is None:
            self.log.error("Failed to connect to %s:%d", self.host, self.port)
            return
        # 1 ) Get package names and versions
        with open(apk_names_list_file, 'r') as f:
            # skip the first line since it's the header line [apk_name, download_count]
            next(f)
            for line in f:
                arr = [items.strip() for items in line.split(',')]
                package_name = arr[0]
                version_code = arr[1]
                result_file_name = os.path.join(os.path.abspath(out_dir),
                                            'views-' + package_name + "-" + 
                                            version_code + ".json")
                json_file = open(result_file_name, 'w')
                cypher_query = ("MATCH (v:VIEW)-[*]-" +
                          "(app:App {name: '" + package_name + "'" + 
                          ", version_code: '" + version_code + "'})" +
                          " RETURN v")
                results = []
                views_list = []
                try:
                    results = graph.cypher.execute(cypher_query)
                except GraphError:
                    self.log.error("Failed to find views for %s-%s. ", package_name, version_code)
                    self.log.exception('')
                for record in results:
                    view = record[0].properties
                    views_list.append(view)
                self.log.info("Writing views for %s-%s. ", package_name, version_code)
                views_json = {"package": package_name, "version_code" : version_code,
                              "views" : views_list}
                json.dump(views_json, json_file, sort_keys= True, indent=4)
                
    
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
        parser = OptionParser(usage = "python %prog <package_names_file> <db_path> [OPTIONS]\n", version = "%prog 1.0")
        '''
        parser.add_option('-H', '--host', dest = "host", default = 'localhost',
                          help = 'the address of the Neo4j Server. Default is localhost.')
        parser.add_option('-p', '--port', dest = "port", type = 'int',
                          help = 'the port number the Neo4j Server is listening on. Default is 7474.')
        '''
        parser.add_option("-l", "--log", dest = "log_file",
                          help = "write logs to FILE.", metavar = "FILE")
        parser.add_option("-o", "--out-dir", dest = "out_dir",
                          help = "write output files to the given DIR. Default is the current working directory.",
                          metavar = "DIR")
        (options, args) = parser.parse_args()
        out_dir = os.path.dirname(os.path.realpath(__file__))
        if len(args) != 2:
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
        '''
        if options.host:
            self.host = options.host
        if options.port:
            self.port = options.port
        '''
        apk_names_list_file = args[0]
        if not os.path.isfile(apk_names_list_file):
            sys.exit("Error: APK names list file " + apk_names_list_file + " does not exist.")
        if not os.path.isdir(args[1]):
            sys.exit("Error: db path doesn't exist. " + options.out_dir + " No such directory.")
        self.db_path = args[1]
        self.find_views(apk_names_list_file, out_dir)
        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
        

if __name__ == '__main__':
    ViewsExtractor().main(sys.argv[1:])
