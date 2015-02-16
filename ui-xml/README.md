# ui-xml
A tool for parsing Android xml layout files and storing them in one XML file to simplify UI analysis. It resolves resource references (e.g., ```@string/cancel_btn```) and embeded layouts (e.g., using the ```<include/>``` and ```<merge/>``` tags).


### Requirements

- This tool works on unpacked apk files. You must use apktool to unpack APK files and decode binary XML files.


### Usage
```
Usage: python ui_xml.py <root_unpacked_apk_directories> [options]

DESCRIPTION: A tool for parsing Android xml layout files and storing them in
one XML file to simplify UI analysis. It resolves resource references (e.g.,
@string/cancel_btn) and embeded layouts (e.g., using the <include/> and
<merge/> tags).

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        increase verbosity.
```

### Example

```
$ ls ~/unpacked-apps
com.alexis.converter-230
com.alexis.converter-261
com.rarepebble-23
com.rarepebble-26

$ python ui_xml.py ~/unpacked-apps
$ ls ~/unpacked-apps/*/ui-xml
com.alexis.converter-230/ui-xml/com.alexis.converter-230.xml
com.alexis.converter-261/ui-xml/com.alexis.converter-261.xml
com.rarepebble-23/ui-xml/com.rarepebble-23.xml
com.rarepebble-26/ui-xml/com.rarepebble-26.xml

```
