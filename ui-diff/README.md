# ui-diff
Tools for extracting the views from neo4j and comparing the views between two app versions.

## 1- views-extractor
This tool extracts the views of a given app version and outputs a text file that
contains the views and their attributes.

### Requirement

  - neo4j server must be running on the default port 7474.
  - You should run [ui-graphdb-writer](../ui-graphdb-writer) to populate the graph database with UI data before using this tool.


### Usage
```
Usage: python views_extractor.py <package_names_file> <db_path> [OPTIONS]


Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -l FILE, --log=FILE   write logs to FILE.
  -o DIR, --out-dir=DIR
                        write output files to the given DIR. Default is the
                        current working directory.
```

## 2- views-diff
This tool compares the views of two app versions and generates a file that contains the views that have been added to the latest version. This tool takes the output of the _views-extractor_ tool as input.

```
Usage: python views_diff.py <old_views_file> <new_views_file> [OPTIONS]


Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -l FILE, --log=FILE   write logs to FILE.
  -o DIR, --out-dir=DIR
                        write output files to the given DIR. Default is the
                        current working directory.
```