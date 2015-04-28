#!/usr/bin/python
import sys
import os
import datetime
import logging
import multiprocessing
from multiprocessing import Pool
from optparse import OptionParser
from subprocess import Popen, PIPE


log = logging.getLogger("grep_input_smali_text_files")
log.setLevel(
    logging.DEBUG)  # The logger's level must be set to the "lowest" level.

# pickled method defined at the top level of a module to be called by multiple processes.
# Runs apktool and returns the directory of the unpacked apk file.
def run_grep(smali_text_file, search_word):
    log.info("Running grep on " + smali_text_file)
    # Run grep -m 1 smali.txt 
    # -m 1 means stop reading the file after 1 matching lines.
    # -l means only returns the file name.
    sub_process = Popen(
        ['grep', '-lm 1', search_word, smali_text_file], stdout=PIPE,
        stderr=PIPE)
    out, err = sub_process.communicate()
    rc = sub_process.returncode
    if rc == 0 and out is not None:
        log.info("Found %s in %s, %s", search_word, smali_text_file, out)
        return (smali_text_file, True)
    if rc != 0:
        log.error('%s is not found in: %s. %s', search_word, smali_text_file,
                  err)
    return (smali_text_file, False)


class GrepInputSmaliTextFiles(object):
    # Set the number of worker processes to the number of available CPUs.
    processes = multiprocessing.cpu_count()

    def __init__(self):
        self.ordered = False

    def start_main(self, search_word, source_dir, target_dir, command):
        pool = Pool(processes=self.processes)
        log.info('A pool of %i worker processes has been created',
                 self.processes)
        count = 0
        smali_methods_file_list = []
        # Iterate over the unpacked apk files in the source directory.
        for smali_file in [os.path.join(source_dir, f) for f in
                           os.listdir(source_dir)]:
            if (smali_file.endswith('.smali.txt')):
                smali_methods_file_list.append(smali_file)
        if len(smali_methods_file_list) > 0:
            try:
                # output file
                result_file_name = os.path.join(target_dir,
                                                'find_' + command + '.csv')
                result_file = open(result_file_name, 'w')
                result_file.write('package,version_code,' + command + '\n')
                # Check if files must be ordered
                if self.ordered:
                    log.info('Sorting the smali text files by modified date.')
                    smali_methods_file_list.sort(
                        key=lambda x: os.path.getmtime(x))
                # Run grep on the each smali text file asynchronously.
                results = [
                    pool.apply_async(run_grep, (smali_text_path, search_word))
                    for smali_text_path in smali_methods_file_list]
                for r in results:
                    if r is not None:
                        (file_name, found) = r.get()
                        file_name = os.path.basename(file_name)
                        package_name = file_name.rsplit('-', 1)[0]
                        version_code = \
                            file_name.rsplit('.smali.txt')[0].rsplit('-')[1]
                        result_file.write(
                            package_name + ',' + version_code + ',' + str(
                                found) + '\n')

                # close the pool to prevent any more tasks from being submitted to the pool.
                pool.close()
                # Wait for the worker processes to exit
                pool.join()
                log.info("The output has been written at: %s", result_file_name)
                result_file.close()
            except KeyboardInterrupt:
                print(
                    'got ^C while worker processes have outstanding work. Terminating the pool and stopping the worker processes immediately without completing outstanding work..')
                pool.terminate()
                print('pool has been terminated.')
        else:
            log.error('Failed to find smali.txt files in %s', source_dir)


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
            usage="python %prog [options] search_word " +
                  "smali_methods_text_files_dir target_dir",
            version="%prog 1.1",
            description='Grep. Searches for words in text files. ' +
                        'This tool recursively ' +
                        'searches for words in smali text files generated ' +
                        'the smali_api_methods tool.')
        parser.add_option("-p", "--processes", dest="processes", type="int",
                          help="the number of worker processes to use. " +
                               "Default is the number of CPUs in the system.")
        parser.add_option('-o', '--ordered', help='Sort apk dirs by date.',
                          dest='ordered', action='store_true', default=False)
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        parser.add_option('-f', '--out-file', dest="out_file_name",
                          help='The name of the output file.')
        (options, args) = parser.parse_args()
        if len(args) != 3:
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
        # Check search word
        command = args[0]
        if options.out_file_name:
            command = options.out_file_name
        if args[0] == 'fragment':
            command = 'fragment'
            args[
                0] = r"Landroid/app/Fragment\|Landroid/app/DialogFragment\|Landroid/app/ListFragment\|Landroid/app/PreferenceFragment\|Landroid/app/WebViewFragment"
        # Check arguments
        if os.path.isdir(args[1]) and os.path.isdir(args[2]):
            self.start_main(args[0], args[1], args[2], command)
        else:
            sys.exit("Error: No such directory.")

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    GrepInputSmaliTextFiles().main(sys.argv[1:])
