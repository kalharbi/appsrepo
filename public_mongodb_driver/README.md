# MongoDB Ruby Driver
This is the MongoDB driver for the database. It retrieves all public descriptions of apps by the permission name and stores the results in text files.
### Usage:

    Usage: ./mongodb_driver.rb {CMD} {out_dir} [OPTIONS]
    CMD: { find_apps_by_permission | find_top_apps | write_description_for_all_apps_with_at_least_one_permission | write_apps_description_by_permission}}
    
    -h, --help                       Show this help message and exit
    -l, --log <log_file,[level]>     Write logs to the specified file with the given logging level such as error or info. The default logging level is info.
    -H, --host <host_name>           The host name that the mongod is connected to. Default value is localhost.
    -p, --port <port>                The port number that the mongod instance is listening. Default port number value is 27017.
    -P, --permission <name>          One valid Android permission name that the application needs.
    -f, --fee <Free|Paid>            The fee to indicate whether to return free or paid apps. Valid values are free or paid
    -m, --max <value>                The maximum number of documents to return.
    -v, --verbose                    Causes the tool to be verbose to explain what is being done.

### Examples:

- Get all public descriptions of Camera apps and save the results in text files at ~/camera_apps_descriptions.

        ruby ./mongodb_driver.rb write_apps_description_by_permission ~/camera_apps_descriptions --permission android.permission.CAMERA

- Get the desciption of all apps with at least one permission and save the results in text files at ~/permission_apps_description/

        ruby ./mongodb_driver.rb write_description_for_all_apps_with_at_least_one_permission ~/permission_apps_description

- Get the top 500 apps with permissions and save the results in a text file at ~/top_apps/

        ruby ./mongodb_driver.rb find_top_apps ~/top_apps --fee free --max 500
		
- Get all free camera apps
    
	    ruby ./mongodb_driver.rb find_apps_by_permission /home/khalid/results/ --fee Free --permission android.permission.CAMERA

- Get all paid apps that require PHONE permission

	    ruby ./mongodb_driver.rb find_apps_by_permission /home/khalid/results/ --fee paid --permission android.permission.PHONE

- Get the top free 2000 apps that require Camera permission and save the results into a text file.

        ruby ./mongodb_driver.rb find_top_apps /Volumes/sdi2/uiver/khalid/top_apps_lists/camera/ -f Free -P android.permission.CAMERA -m 2000 -v

- Get the bottom free 2000 apps that require Phone permission and save the results into a text file.
            
        ruby ./mongodb_driver.rb find_bottom_apps /Volumes/sdi2/uiver/khalid/bottom_apps_lists/phone/ -f Free -P android.permission.CALL_PHONE -m 2000 -v

