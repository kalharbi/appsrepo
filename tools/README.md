Tools for Batch Processing APK Files
====================================
Python & shell script tools for batch processing a list of apk files.

####Why?
Running one program multiple times to process a single apk file each time takes a lot of time. 
These tools are used to batch process apk files at once saving me a lot of time.

##Tools:
1. Apktool Executor  *[apktool_executor.py]*
2. Dare Executor  *[dare_executor.sh]*
3. Rename apk Files *[rename_apk_files.py.py]*
4. Find and Copy apk Files *[find_nd_copy.py]*

###1- Apktool Executor  *[apktool_executor.py]*
A python script that runs [apktool]('https://code.google.com/p/android-apktool/') on a group of apps. It takes a text file that contains 
a list of apk names as input, finds their apk files, runs apktool on each apk file, 
and stores the extracted files for each apk file into one directory.

#### Dependencies
*  [apktool version 2.0.0-Beta9]('http://connortumbleson.com/2014/02/apktool-2-0-0-beta-9-released/') or higher. For installation instructions, see [install apktool.]('https://code.google.com/p/android-apktool/wiki/Install')

#### Usage:

```
Usage: python apktool_executor.py apk_source_directory target_directory [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -p PROCESSES, --processes=PROCESSES
                        the number of worker processes to use. Default is the
                        number of CPUs in the system.
  -w FRAMEWORK_DIR, --framework=FRAMEWORK_DIR
                        forces apktool to use framework files located in
                        <FRAMEWORK_DIR>.
  -t TAG, --tag=TAG     forces apktool to use framework files tagged by <TAG>.
  -s, --no-src          Do not decode sources.
  -r, --no-res          Do not decode resources.
  -l FILE, --log=FILE   write logs to FILE.
  -v, --verbose         increase verbosity.
  -f FILE, --file=FILE  read apk names from a file that contains a list of APK
                        names.
  -c, --custom          search for apk files using the custom directory naming
                        scheme. e.g, dir/c/com/a/amazon/com.amazon
```
#### Example:
``` python apktool_executor.py ~/apk_files/ ~/unpacked/ -t nexus10 -l ./log_apktool.log ```
###2- Dare Executor  *[dare_executor.sh]*
A shell script that runs [dare]('http://siis.cse.psu.edu/dare/') on a group of apps.

#### Usage:

```
Usage: sh dare_executor.sh input_directory_that_contains_apk_files output_directory
```
__Note:__ You have to edit the file dare_executor.sh and change the DARE_PATH variable to point to the location where dare is installed.

###3- Rename apk Files *[rename_apk_files.py.py]*
A Python script that renames a list of apk files using package and version code naming convention (e.g., packageName-versionCode.apk).

#### Usage:

```
Usage: python rename_apk_files.py apk_files_directory [options]

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        increase verbosity.
  
```
###4- Find and Copy apk Files *[find_nd_copy.py]*
A Python script that finds apk files and copies them into one directory. It takes a text file that contains 
a list of apk names as input, finds their apk files, and copies them into the given target directory.

#### Usage:

```
Usage: python find_nd_copy.py [options] apk_names_file source_directory target_directory

apk_names_file is a file that contains comma separtaed apk name values like the example below:
            apk_name,
            com.evernote,
            com.google.android.apps.maps,

source_directory is where the actual files are stored.
target_directory is the destination to copy the files to.

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        Increase verbosity.
```
