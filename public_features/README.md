## Public Features Collection
Store apps' public features into Mongodb.

### Requirements
* Required:
  * Ruby 1.9 or later.
  * Mongodb 2.4.6 or later.
  * gem install mongo.
  * gem install bson.
* Recommended:
  * gem update --system
  * gem install bson_ext

### Usage:
```
   Usage: public_main.rb {json_file | json_directory} [OPTIONS]
   Optional arguments: 
         -h, --help                       Show this help message and exit.
         -l, --log <log_file,[level]>     Write logs to the specified file with the given logging level such as error or info. The default logging level is info.
         -H, --host <host_name>           The host name that the mongod is connected to. Default value is localhost.
         -v, --verbose                    Causes the tool to be verbose to explain what is being done, showing .json files as they are processed.
```

##Public Features Collection
###Fields Names:
Field names consume disk space, so we should keep them short but still meaningful.

|short name |  meaning                  |
|-----------|---------------------------|
| n         | apk name                  |
| t         | app title                 |
| desc      | description               |
| url       | play store URL            |
| cat       | category                  |
| pr        | price                     |
| dp        | date published            |
| ver       | version                   |
| os        | operating systems         |
| ratc      | ratings count             |
| rat       | rating                    |
| crat      | content rating            |
| cre       | creator                   |
| curl      | creator URL               |
| sz        | install size              |
| szt       | install size text         |
| dowc      | downloads count           |
| dowt      | downloads count text      |
| per       | permissions               |
| rev       | reviews                   |
| ts        | review time stamp in Msec |
| st        | review star rating        |
| t         | review title              |
| cmt       | review comment            |
| id        | review comment id         |
| a         | review author             |
| url       | review author URL         |
| surl      | review author secure URL  |

