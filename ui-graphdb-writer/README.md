#ui-graphdb-writer
The goal of this tool is to import GraphML files into neo4j database. It takes as an input the output of the [ui-graphml](../ui-graphml) tool which contains the UI of Android apps in GraphML format and generates a shell script that imports the UI of apps that don't exist in neo4j.

### Requirements
- Java 1.7
- neo4j 2.1.5 or higher. neo4j must be defined in PATH
- [neo4j-shell-tools](https://github.com/jexp/neo4j-shell-tools). neo4j-shell must be defined in PATH


### Before you run the tool
- Make sure that you run the [ui-graphml](../ui-graphml) tool on the unpacked apk files before using this tool.
- Make sure that neo4j server is not running ```neo4j stop```.

### After you run the tool
- start neo4j ```{NEO4J_HOME}/bin/neo4j start```
- Make sure that ```neo4j``` and ```neo4j-shell``` is defined in your PATH
- The tool will output a shell bash script file that you need to run using:
  -  ```sh PATH_TO_PATH_SCRIPT```

###Usage:
```
Usage: ui-graphdb-writer [options] unpacked_apks_path
  Options:
  * -b, -db-path
       the location of neo4j's database directory.
    -h, -help
       print help and exit.
       Default: false
    -l, -log
       Write error level logs to DIR.
    -v, -version
       Prints version and exit
       Default: false
	   
```

### Example:

```java -jar ui-graphdb-writer.jar ./unpacked-apks/ -b ~/neo4j-data/```

The tool will create a shell script file that can be run to start importing into neo4j using:

```sh /tmp/org.bigdiff.ui-graphdb-writer592050904916352248.sh```