#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require 'mongo'
require 'optparse'
require 'logger'
require_relative 'app'
require_relative 'json_reader'

class PublicMain
  @@log = Logger.new(STDOUT)
  @@log.level = Logger::INFO
  @@usage = "Usage: #{$PROGRAM_NAME} {json_file | json_directory}"
  DB_NAME = "apps"
  COLLECTION_NAME = "public"
  
  private
  def connect_mongodb
    mongo_client = Mongo::Connection.new
    db = mongo_client.db(DB_NAME)
    collection = db.collection(COLLECTION_NAME)
    @@log.info("Connected to database: #{DB_NAME}, collection: #{COLLECTION_NAME}")
    collection
  end

  def insert_document(collection, document)
    id = collection.insert(document)
  end

  def document_reader(collection, json_file)
    json_reader = JsonReader.new
    app_info = json_reader.parse_json_data(json_file)
    id = insert_document(collection, app_info)
    @@log.info("Inserted a new document for apk #{app_info["name"]}, document id = #{id}")
  end
  
  def start_main(source)
    if(!File.exist? source)
      puts "Error: No such file or directory"
      abort(@@usage)
    elsif(File.directory?(source))
      if(Dir[source + '/*.json'].empty?)
        puts "The specified directory does not contain .json file(s)."
        abort(@@usage)
      end
      collection = connect_mongodb
      # If the source is a directory that contains json file(s).
      Dir.glob(source + '/*.json') do |json_file|
        document_reader(collection, json_file)
      end
     # If the source is a json file
    elsif (File.extname(source).downcase.eql? ".json")
      collection = connect_mongodb
      document_reader(collection, source)
    else
      abort(@@usage)
    end
  end

  public
  def command_line(args)
    opt_parser = OptionParser.new do |opts|
      opts.banner = @@usage
      opts.on('-h', '--help', 'Show this help message and exit') do
        puts opts
        exit
      end
      opts.on('-l', '--logfile FILE', 'Write log to the specified FILE') do |file_name|
        file = File.open(file_name, File::WRONLY | File::APPEND | File::CREAT)
        @@log = Logger.new(file)
        @@log.level = Logger::INFO
      end
    end
    opt_parser.parse!

    if(args[0].nil?)
      abort(@@usage)
    else
      source = File.absolute_path(args[0])
      start_main(source)
    end
  end
end

if __FILE__ == $PROGRAM_NAME
  main_obj = PublicMain.new
  main_obj.command_line(ARGV)
end
