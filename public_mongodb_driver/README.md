# MongoDB Ruby Driver
MongoDB driver for the public features collection. It retrieves public features of apps by permission name and stores the results in text files.
### Usage:
Usage: ruby mongodb_driver.rb <command> <out_dir> [OPTIONS]


```

Usage: ruby ./mongodb_driver.rb <command> <out_dir> [OPTIONS]

The following commands are available:

    find_apps_by_permission -P <permission_name> 
    find_top_apps
    find_bottom_apps  
    find_top_bottom_apps_in_any_permission -P <comma_separated_permission_names>
    find_top_bottom_apps_not_in_any_permission -P <comma_separated_permission_names>
	write_description_for_all_apps_with_at_least_one_permission
    write_apps_description_by_permission -P <permission_name>
    write_apps_description_by_package_name -k <file_names_of_packages>
	find_version_code -k <file_names_of_packages>
    find_app_info -k <file_names_of_packages_and_code_versions>

 The following options are available:

    -h, --help                       Show this help message and exit
    -l, --log <log_file,[level]>     Write logs to the specified file with the given logging level
                                     such as error or info. The default logging level is info.
    -H, --host <host_name>           The host name that the mongod is connected to. Default value
                                     is localhost.
    -p, --port <port>                The port number that the mongod instance is listening. Default port
                                     number value is 27017.
    -P, --permission <name>          One valid Android permission name that the application uses,or a
                                     list of comma separated permissions that the app may use (inclusive disjunction).
    -k, --package <pckg_list_file>   File that contains a list of package names.
    -f, --fee <Free|Paid>            The fee to indicate whether to return free or paid apps.
                                     Valid values are free or paid
    -m, --max <value>                The maximum number of documents to return.
    -v, --verbose                    Causes the tool to be verbose to explain what is being done.

```

### Examples:

1. Get all public descriptions of Camera apps and save the results in text files at ~/camera_apps_descriptions.

        ruby ./mongodb_driver.rb write_apps_description_by_permission ~/camera_apps_descriptions --permission android.permission.CAMERA

2. Get the desciption of all apps with at least one permission and save the results in text files at ~/permission_apps_description/

        ruby ./mongodb_driver.rb write_description_for_all_apps_with_at_least_one_permission ~/permission_apps_description

3. Get the top 500 apps with permissions and save the results in a text file at ~/top_apps/

        ruby ./mongodb_driver.rb find_top_apps ~/top_apps --fee free --max 500
		
4. Get all free camera apps
    
	    ruby ./mongodb_driver.rb find_apps_by_permission /home/khalid/results/ --fee Free --permission android.permission.CAMERA

5. Get all paid apps that require PHONE permission

	    ruby ./mongodb_driver.rb find_apps_by_permission /home/khalid/results/ --fee paid --permission android.permission.PHONE

6. Get the top free 2000 apps that require Camera permission and save the results into a text file.

        ruby ./mongodb_driver.rb find_top_apps /Volumes/sdi2/uiver/khalid/top_apps_lists/camera/ -f Free -P android.permission.CAMERA -m 2000 -v

7. Get the bottom free 2000 apps that require Phone permission and save the results into a text file.
      
        ruby ./mongodb_driver.rb find_bottom_apps /Volumes/sdi2/uiver/khalid/bottom_apps_lists/phone/ -f Free -P android.permission.CALL_PHONE -m 2000 -v

8. Get the top and bottom 100 free apps that make use of any of the following Bluetooth related permissions: android.permission.BLUETOOTH,android.permission.BLUETOOTH_ADMIN,android.permission.BLUETOOTH_PRIVILEGED

        ruby ./mongodb_driver.rb find_top_bottom_apps_in_any_permission ./ -v -l ./either_in.log -f Free -m 100 -P android.permission.BLUETOOTH,android.permission.BLUETOOTH_ADMIN,android.permission.BLUETOOTH_PRIVILEGED

9. Get the top and bottom 100 free apps that DO NOT use any of the following Bluetooth related permissions: android.permission.BLUETOOTH,android.permission.BLUETOOTH_ADMIN,android.permission.BLUETOOTH_PRIVILEGED

        ruby ./mongodb_driver.rb find_top_bottom_apps_not_in_any_permission ./ -v -l,error ./neither_in.log -f Free -m 100 -P android.permission.BLUETOOTH,android.permission.BLUETOOTH_ADMIN,android.permission.BLUETOOTH_PRIVILEGED

10. Get the version code for a list of package names. Get a maximum of two versions per package name. [We will use the output of the example above (#10) as the input file]

        ruby ./mongodb_driver.rb find_version_code ./ -k bottom_either_free-BLUETOOTH-BLUETOOTH_ADMIN-BLUETOOTH_PRIVILEGED-apps.txt -m 2 -v -l ./log-version-finder.log,error
