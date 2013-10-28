#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require 'mongo'
require 'optparse'
require_relative 'app'
require_relative 'json_reader'

DB_NAME = "apps"
COLLECTION_NAME = "public"

def connect_mongo()
  mongo_client = Mongo::Connection.new
  db = mongo_client.db(DB_NAME)
  collection = db.collection(COLLECTION_NAME)
end

def insert_document(collection, document)
  id = collection.insert(document)
end

$usage = "Usage: #{$PROGRAM_NAME} {json_file | json_directory}"

opt_parser = OptionParser.new do |opts|
  opts.banner = $usage
  opts.on('-h', '--help') do
    puts opts
    exit
  end
  opts.on('-l', '--logfile FILE', 'Write log to FILE') do |file|
    $log_file = file
  end
end
opt_parser.parse!

collection = connect_mongo()

def do_main(json_file)
  json_reader = JsonReader.new
  app = json_reader.parse_json_data(json_file)
  id = insert_document(collection, app.to_json)
  puts "Inserted document - #{id}\n"
end

if(ARGV[0].nil?)
  abort($usage)
end

source = File.absolute_path(ARGV[0])

if(!File.exist? source)
  puts "Error: No such file or directory"
  abort($usage)
elsif(File.directory?(source))
  if(Dir[source + '/*.json'].empty?)
    puts "The specified directory does not contain .json file(s)."
    abort($usage)
  end
  # If the source is a directory that contains json file(s).
  Dir.glob(source + '/*.json') do |json_file|     
  do_main(json_file)
  end
  # If the source is a json file
elsif (File.extname(source).downcase.eql? ".json")
  do_main(source)
else
  abort($usage)
end

