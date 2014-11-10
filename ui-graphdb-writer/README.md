#ui-graphdb-writer
Android UI GraphDB writer is a tool for importing GraphML file format into neo4j database. 
It takes as an input the output of [the ui-graphml tool](../ui-graphml) which contains the UI of Android apps in GraphML files and loads it into neo4j.

### Requirement 
- Java 1.7
- neo4j 2.1.5 or higher. neo4j must be defined in PATH
- [neo4j-shell-tools](https://github.com/jexp/neo4j-shell-tools). neo4j-shell must be defined in PATH


### Before you start the tool
Make sure that you ran the [the ui-graphml tool](../ui-graphml) on the unpacked apk files before using this tool.

### After you run the tool
- start neo4j ```{NEO4J_HOME}/bin/neo4j restart```
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