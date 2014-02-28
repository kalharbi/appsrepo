## Smali Method Names Extraction

The goal of this tool is to extract Android API methods and user's defined methods from .smali files.
The results are saved at [apk-name]/methods

## Usage:

    smali_methods_finder.rb dir_to_unpacked_apks [OPTIONS]
    -h, --help                       Show this help message and exit.
    
    -l, --log <log_file,[level]>     Write logs to the specified file with the given logging level such as error or info. The default logging level is info.
    
    -f <find_app_methods | find_invoked_api_methods>,
        --find                       The running mode. It must be one of the following: find_app_methods or find_invoked_api_methods. The default mode is to find both user's declared methods and Android API methods.
