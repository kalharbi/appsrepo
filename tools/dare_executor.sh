#!/bin/bash
IN_DIR=$1
OUT_DIR=$2
PROGNAME=`basename $0`
DARE_PATH='/home/khalid/dare/dare-1.1.0-linux/dare'

usage(){
	echo 'Usage: ' $PROGNAME '<input_directory> <output directory>'
	exit 1
}

run_tool(){
	for file in $IN_DIR*.apk
	  #echo $file
	do
		file_name=$(basename "$file")
		target_name="${file_name%.*}"
		target_directory=$OUT_DIR$target_name
		echo 'mkdir ' $target_directory
		mkdir $target_directory
		echo $DARE_PATH '-d' $target_directory $file
		$DARE_PATH '-d' $target_directory $file
		echo '====================================='
	done
}

# call usage() function if arguments are not supplied
[[ $# -eq 0 ]] || [[ $# -eq 1 ]] && usage

# Check if the supplied directories exist
if [ -d $IN_DIR ]  && [ -d $OUT_DIR ]
	then 
	    run_tool
elif [ ! -d $IN_DIR ]
	then
	    echo "Error: No such directory: $IN_DIR"
	    usage
elif [ ! -d $OUT_DIR ]
	then
		echo "Error: No such directory: $OUT_DIR"
		usage
fi
