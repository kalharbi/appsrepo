# APK Files Bucket
## Retrieve APK Files from MongoDB GridFS

This is a Java based tool that retrives APK files from MongoDB bucket and saves them into a directory.


## Requirements
-  Apache Maven 3 or higher.

## Build Instructions

``` mvn package ```

## Usage

```

usage: java -jar apk_retrieval_jGridFS-0.0.1-SNAPSHOT.jar{ {package_name version_code} | package_list_file } target_directory 

[OPTIONS] [-help] [-version]

       
Retrieves APK files from MongoDB bucket and saves them into target_directory.
       
package_name: Android app package name.
version_code: Android app version code value.
package_list_file: A CSV file that contains package names and version code numbers.
       
Example usage:
java -jar apk_retrieval_jGridFS-0.0.1-SNAPSHOT.jar com.evernote 1057013 ~/target_dir
       
OR
       
java -jar apk_retrieval_jGridFS-0.0.1-SNAPSHOT.jar list_file.csv ~/target_dir
       list_file.csv:
                     package_name,version_code
                     com.evernote,1057013
                     .....
	  

```
