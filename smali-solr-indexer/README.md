#smali-solr-indexer
Indexing apps' smali invoked methods in Apache Solr.

This tool takes a directory of text files that contains smali invoked methods
and index them with Solr Cell using Apache Tika via HTTP POST request. Smali
text files must be named as packageName-versionCode.smali.txt (e.g., com.android.app-123.smali.txt)

## Before Running the tool

1. Run the [smali-invoke-methods tool](../smali-methods-finder/) on the decoded (unpacked) apk files.
2. Add new fields into Solr's documents:

```
curl -X POST -H 'Content-type:application/json' --data-binary '{ "add-field":{ "name":"package_name", "type":"string", "indexed":true, "required":true, "stored":true } }' http://localhost:8983/solr/sievely-code/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{ "add-field":{ "name":"version_code", "type":"int", "indexed":true, "required":true, "stored":true } }' http://localhost:8983/solr/sievely-code/schema
```

## Usage
```
Usage: python smali_solr_indexer.py smali_invoke_dir [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -l FILE, --log=FILE   write logs to FILE.
  -v, --verbose         Increase verbosity.
  -H HOST_NAME, --hostname=HOST_NAME
                        Solr host name
  -p PORT_NUMBER, --port=PORT_NUMBER
                        Solr port number
  -c COLLECTION_NAME, --collection=COLLECTION_NAME
                        Solr collection name
```