appsrepo
========

A tool chain that extracts, analyzes, loads, and retrives real Android apps.

### 1- [Public Features MongoDB Ruby Driver](public_mongodb_driver/)
This is the Ruby MongoDB driver for the public collection of the database. It retrieves various public information of apps and stores the results in text files.

### 2- [Public Features Collection](public_features/)
This tool reads raw JSON files and stores them into a MongoDB collection named public.

### 3- [Smali Methods Finder](smali-methods-finder/)
This is a Ruby based tool that extracts Android API methods and user's defined methods from .smali files.

### 4- [Manifest Features Collection](manifest_features/)
This tool parses AndroidManifest.xml files and stores them into a MongoDB collection named manifest.

### 5- [Manifest Mongodb Driver](manifest_mongodb_driver/)
This is the Python MongoDB driver for the manifest collection of the database. It retrieves AndroidManifest features from MongoDB and stores the results into text files.

### 6- [Tools](tools/)
Python & shell script tools for batch processing a list of apk files.

