appsrepo
========

A tool chain that extracts, analyzes, loads, and retrives Android apps.

### 1- [APK Bucket](apk_bucket/)
This includes a Python tool that stores apk files in a common MongoDB bucket using GridFS, and a Java based tool that retrieves them.

### 2- [Public Features MongoDB Ruby Driver](public_mongodb_driver/)
This is the Ruby MongoDB driver for the public collection of the database. It retrieves various public information of apps and stores the results in text files.

### 3- [Public Features Collection](public_features/)
This tool reads raw JSON files and stores them into a MongoDB collection named public.

### 4- [Smali Methods Finder](smali-methods-finder/)
This is a Ruby based tool that extracts Android API methods and user's defined methods from .smali files.

### 5- [Manifest Features Collection](manifest_features/)
This tool parses AndroidManifest.xml files and stores them into a MongoDB collection named manifest.

### 6- [Manifest Mongodb Driver](manifest_mongodb_driver/)
This is the Python MongoDB driver for the manifest collection of the database. It retrieves AndroidManifest features from MongoDB and stores the results into text files.

### 7- [Tools](tools/)
Python & shell script tools for batch processing a list of apk files.

- - -

## Sample APK Files
- 10 apps, two versions each, sdk target 17 [Download]('https://drive.google.com/file/d/0Byamwcm0_ml5SjJvZlpNV2lERkk/edit?usp=sharing')
- 100 apps, two versions each [Download]('https://drive.google.com/file/d/0Byamwcm0_ml5SUhUTTdTZUVIYmc/edit?usp=sharing')
- Android Framework files for the following devices: Samsung Galaxy S3, Google Nexus 10, and Google Nexus5. [Download]('https://drive.google.com/file/d/0Byamwcm0_ml5SFpVclR3YzlvZms/edit?usp=sharing')

