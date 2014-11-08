## Android UI GraphML Writer
This is a tool for writing and representing the UIs of Android apps in
a GraphML format, a file format for graphs. It parses layout and resources files, identifies the
relationships between UI components, stores the result in a GraphML file that
describes the structural properties of the UI. The GraphML file can be imported into the tinkerpop stack or any graph databse (e.g, neo4j, titan, etc).

### Build and Usage

#### Build the project using maven

```
mvn package
cd target
```

#### Usage
```
usage: java -jar ui-graphml-{version}.jar <unpacked_apks_dir> [OPTIONS]

OPTIONS:
 -help             print help info.
 -l,--log <FILE>   Write logs to FILE.
 -version          print the version number.

```

The results are saved using the following file naming scheme

```unpacked_dir/ui-graphml/package_name-version_code.graphml```

