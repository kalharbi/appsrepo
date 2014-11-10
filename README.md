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

### 7- [Android UI GraphML Writer](ui-graphml/)
This tool writes the UIs of Android apps in a GraphML format, a file format for graphs. It parses layout and resources files, 
identifies the relationships between UI components, stores the result in a GraphML file that describes the structural properties of the UI.
The GraphML file can be imported into the tinkerpop stack or any graph databse (e.g, neo4j, titan, etc).

### 8- [Android UI GraphDB Writer](ui-graphdb-writer/)
This tool takes the input of the Android UI GraphML Writer (#7) as an input and loads it into the graph database (neo4j).

### 9- [Tools](tools/)
Python & shell script tools for batch processing a list of apk files.

- - -

## Sample APK Files
- 10 apps, two versions each, target sdk 17. [Download](https://drive.google.com/uc?export=download&id=0Byamwcm0_ml5SjJvZlpNV2lERkk)
- 7 apps, two versions each, target sdk 16. [Download](https://drive.google.com/uc?export=download&id=0Byamwcm0_ml5d3licGJYOVBlb28)
- 9 apps, two versions each, target sdk 14. [Download](https://drive.google.com/uc?export=download&id=0Byamwcm0_ml5bHlrOVQ1SlhTcVE)
- 10 apps, two versions each, minimum sdk 8. [Download](https://drive.google.com/uc?export=download&id=0Byamwcm0_ml5bm54WGtFa185TTA)
- 100 apps, two versions each. [Download](https://drive.google.com/uc?export=download&id=0Byamwcm0_ml5SUhUTTdTZUVIYmc)
- Android Framework files for the following devices: Samsung Galaxy S3, Google Nexus 10, and Google Nexus5. [Download](https://drive.google.com/uc?export=download&id=0Byamwcm0_ml5SFpVclR3YzlvZms)

