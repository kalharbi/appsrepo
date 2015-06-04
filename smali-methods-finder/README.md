## Smali Method Names Extraction

The goal of this tool is to extract Android API methods and user's defined methods from .smali files.
The results are saved at [apk-name]/methods

## smali\_invoked\_methods
This tool recursively searches for invoke- methods calls and store them in one
text file.

### Usage:


```
Usage: python smali_invoked_methods.py unpacked_apk_dir target_dir [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -p PROCESSES, --processes=PROCESSES
                        the number of worker processes to use. Default is the
                        number of CPU cores.
  -l FILE, --log=FILE   write logs to FILE.
  -v, --verbose         Increase verbosity.
  -d DEPTH_VALUE, --depth=DEPTH_VALUE
                        The depth of the child directories to scan for
                        AndroidManifest.xml files. Default is: 1
```
