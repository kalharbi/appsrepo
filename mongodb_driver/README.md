# MongoDB Ruby Driver
This is the MongoDB driver for the database. It retrieves all public descriptions of apps by the permission name and stores the results in text files.
### Usage:

    Usage: ./mongodb_driver.rb {out_dir} [OPTIONS]
    
    -h, --help                       Show this help message and exit.
    
    -l, --log <log_file,[level]>     Write logs to the specified file with the given logging level such as error or info. The default logging level is info.
    
    -H, --host <host_name>           The host name that mongod is connected to. Default value is localhost.
    
    -p, --port <port>                The port number that mongod instance is listening to. Default port number value is 27017.
    
    -P, --permission <name>          One valid Android permission name that the application needs.
    
    -v, --verbose                    Causes the tool to be verbose to explain what is being done.

### Examples:
-   Get all public descriptions of Camera apps and save the results in text files at ~/camera_apps_descriptions.

        ruby ./mongodb_driver.rb ~/camera_apps_descriptions --permission android.permission.CAMERA

- Get the desciption of all apps with permissions and save the results in text files at ~/permission_apps_description/

        ruby ./mongodb_driver.rb ~/permission_apps_description
