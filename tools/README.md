Tools for Batch Processing APK Files
====================================
Python & shell script tools for batch processing a list of apk files.

####Why?
Running one program multiple times to process one apk file each time takes a lot of time. 
These tools are used to batch process apk files at once saving you a lot of time.

##Tools:
1. Apktool Executor  *[apktool_executor.py]*
2. Dare Executor  *[dare_executor.sh]*
3. Find and Copy Apk Files *[find_nd_copy.py]*

###1- Apktool Executor  *[apktool_executor.py]*
A python script that runs [apktool]('https://code.google.com/p/android-apktool/') on a group of apps. It takes a text file that contains 
a list of apk names as input, finds their apk files, runs apktool on each apk file, 
and stores the extracted files for each apk file into one directory.

#### Usage:

```
Usage: apktool_executor.py [options] apk_names_file source_directory target_directory

   Options:
     --version            show program's version number and exit
     -h, --help           show this help message and exit
     -l FILE, --log=FILE  write logs to FILE.
     -v, --verbose        Increase verbosity.
     -c, --custom         search for apk files using the custom directory naming
                          scheme. e.g, dir/c/com/a/amazon/com.amazon
```

###2- Dare Executor  *[dare_executor.sh]*
A shell script that runs [dare]('http://siis.cse.psu.edu/dare/') on a group of apps.

#### Usage:

```
Usage: dare_executor.sh input_directory_that_contains_apk_files output_directory
```
__Note:__ You have to edit the file dare_executor.sh and change the DARE_PATH variable to point to the location where dare is installed.

###3- Find and Copy Apk Files *[find_nd_copy.py]*
A Python script that finds apk files and copies them into one directory. It takes a text file that contains 
a list of apk names as input, finds their apk files, and copies them into the given target directory.

#### Usage:

```
Usage: find_nd_copy.py [options] apk_names_file source_directory target_directory

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        Increase verbosity.
```
