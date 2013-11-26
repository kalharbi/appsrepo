#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require 'mongo'
require 'optparse'
require_relative 'app'
require_relative 'json_reader'
require_relative 'files_finder'
require_relative 'logging'

class PublicMain

  @@usage = "Usage: #{$PROGRAM_NAME} {json_file | json_directory} [OPTIONS]"
  DB_NAME = "apps"
  COLLECTION_NAME = "public"
  attr_reader :host, :port, :verbose

  def initialize
    @host = "localhost"
    @port = 27017
    @verbose = false
  end
  
  private
  def connect_mongodb
    mongo_client = Mongo::Connection.new(@host, @port)
    db = mongo_client.db(DB_NAME)
    collection = db.collection(COLLECTION_NAME)
    Logging.logger.info("Connected to database: #{DB_NAME}, collection: #{COLLECTION_NAME}")
    collection
  end

  def insert_document(collection, document)
    id = collection.insert(document)
  end

  def document_reader(collection, json_file)
    json_reader = JsonReader.new
    Logging.logger.info("processing #{json_file}")
    app_info = json_reader.parse_json_data(json_file)
    if !app_info.nil?
      id = insert_document(collection, app_info)
      Logging.logger.info("Inserted a new document for apk: #{app_info["n"]}, document id = #{id}")
    end
  end
  
  def start_main(source)
    puts source
    if(!File.exist? source)
      puts "Error: No such file or directory"
      abort(@@usage)
    elsif(File.directory?(source))
      puts "Searching for .json files at #{source}"
      json_files = FilesFinder.new(source, '.json').find_files(@verbose)
      if(json_files.nil?)
        puts "The specified directory does not contain .json file(s)."
        abort(@@usage)
      end
      collection = connect_mongodb
      # If the source is a directory that contains json file(s).
      json_files.each do |json_file|
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
    begin
      opt_parser = OptionParser.new do |opts|
        opts.banner = @@usage
        opts.on('-h','--help', 'Show this help message and exit.') do
          puts opts
          exit
        end
        opts.on('-l','--log <log_file>', 'Write log to the specified file.') do |file_name|
	  configuration = {"logdev"=> file_name}
	  Logging.config_log(configuration)
        end
        opts.on('-H','--host <host_name>', 'The host name that the mongod is connected to. Default value is localhost.') do |host_name|
          @host = host_name
        end
        opts.on('-p','--port <port>', 'The port number that the mongod instance is listening. Default port number value is 27017.') do |port_num|
          @port = port_num
        end
	opt.on('-v', '--verbose', 'Causes the tool to be verbose to explain what is being done, showing .json files as they are processed') do
	  @verbose = true
	end
      end
      opt_parser.parse!
    rescue OptionParser::AmbiguousArgument
      puts "Error: illegal command line argument."
      puts opt_parser.help()
      exit
    rescue OptionParser::InvalidOption
      puts "Error: illegal command line option."
      puts opt_parser.help()
      exit
    end
 
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
