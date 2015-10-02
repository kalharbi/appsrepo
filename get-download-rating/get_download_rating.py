#!/usr/bin/python
import sys
import os.path
import datetime
import logging
from io import StringIO
import json
import locale
from lxml import etree
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from requests.exceptions import ReadTimeout
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import RequestException
from optparse import OptionParser

class GetDownload(object):

    log = logging.getLogger("get_download_rating")
    log.setLevel(logging.DEBUG)
    DOWNLOAD_COUNT_TEXT_XPATH = ['//div[@itemprop="numDownloads"]/text()']
    RATING_COUNT_XPATH = ['//span[@class="reviews-num"]/text()']
    RATING_XPATH = ['//div[@class="score-container-star-rating"]/div/@aria-label']
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    def start_main(self, package_names_file, target_file):
        with open(target_file, 'w') as out_file:
            out_file.write("[" + "\n")
            with open(package_names_file, 'r') as f:
                for line in f:
                    arr = [items.strip() for items in line.split(',')]
                    package_name = arr[0]
                    app = self.get_app(package_name.strip())
                    if app is not None:
                        out_file.write(app + ",\n")
            out_file.write("]" + "\n")

    def get_app(self, package_name):
        try:
            play_url = "https://play.google.com/store/apps/details?id=" + \
                       package_name
            r = requests.get(play_url)
            if r.status_code == 200:
                html_content = StringIO(requests.get(play_url).text)
                parser = etree.HTMLParser()
                tree = etree.parse(html_content, parser)
                if tree.getroot() is None:
                    self.log.error("Invalid html content for " + package_name)
                    return None
                rating_count_text = self.get_property(tree,
                                                      self.RATING_COUNT_XPATH)
                rating_count = 0
                if rating_count_text != '':
                    rating_count = locale.atoi(rating_count_text)
                rating_text = self.get_property(tree, self.RATING_XPATH)
                rating = 0
                if rating_text != '':
                    rating = float(rating_text.split()[1])
                download_count_text = self.get_property(tree, self.DOWNLOAD_COUNT_TEXT_XPATH)
                download_count = 0
                if download_count_text != '':
                    download_count = locale.atoi(download_count_text.split("-")[0].strip())
                app = json.dumps({"n": package_name,
                                 "rct": rating_count,
                                 "rate": rating,
                                 "dct": download_count},
                                 sort_keys=True,
                                 indent=4,
                                 separators=(',', ': '))
                return app

            else:
                self.log.error("Failed to request the html page for %s " +
                               "http request status code: %i", package_name,
                               r.status_code)
                return None
        except (ConnectionError, HTTPError, Timeout, ReadTimeout) as e:
            self.log.error("Network error while requesting the html page for" +
                           " %s message: %s", package_name, e)
            return None
        except (ChunkedEncodingError, RequestException) as e:
            self.log.error("HTTP request error", e)
            return None

    @staticmethod
    def get_property(tree, xpath_expressions):
        val = None
        for exp in xpath_expressions:
            val = tree.xpath(exp)
            if val:
                break
        return ' '.join(val).strip()

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
        parser = OptionParser(usage="%prog [options] package_names_file target_file", version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        (options, args) = parser.parse_args(argv)
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            logging_file = logging.FileHandler(options.log_file, mode='a',
                                               encoding='utf-8', delay=False)
            logging_file.setLevel(logging_level)
            logging_file.setFormatter(formatter)
            self.log.addHandler(logging_file)
        # Get apk file names
        package_names_file = os.path.abspath(args[0])
        target_file = os.path.abspath(args[1])
        # Check target directory
        if not os.path.exists(package_names_file) or not \
                os.path.isfile(package_names_file):
            sys.exit("Error: package file  " + package_names_file +
                     " does not exist.")
        if os.path.exists(args[1]):
            sys.exit("Error: target file " + target_file +
                     " already exists.")

        self.start_main(package_names_file, target_file)

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    GetDownload().main(sys.argv[1:])
