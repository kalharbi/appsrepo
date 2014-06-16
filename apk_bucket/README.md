# APK Files Bucket
A Python tool that stores apk files in a common MongoDB bucket using GridFS.
The tools creates two collections for this bucket named:

*  __apk.chunks__: The chunks collection contains the actual apk files data.
*  __apk.files__: The files collection contains the apk files metadata. 
   *  The following metadata are stored for each apk file: 
   
        | short name   | meaning         |
        |--------------|-----------------|
        | metadata.n   | package name|
        | metadata.verc| version code|
        | metadata.vern| version name|
        | chunkSize    | The size of each chunk|
        | contentType  | the file type [apk]|
        | filename     | the file name of the document|
        | length       | The size of the document in bytes|
        | uploadDate   | the  date the document was first stored by GridFS|
        | md5          | MD5 hash of the stored apk file|
              

## Usage

```
Usage: python apk_bucket.py apk_files_directory [options]


Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        increase verbosity.

```
