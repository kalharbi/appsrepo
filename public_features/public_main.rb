#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require 'mongo'
require 'optparse'
require_relative 'app'
require_relative 'json_reader'
require_relative 'files_finder'
require_relative '../utils/logging'

class PublicMain

  @@usage = "Usage: #{$PROGRAM_NAME} {InsertWithDuplicates | InsertIfNotExists} {json_file | json_directory} [OPTIONS]"
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

  def insert_document_with_duplicates(collection, document)
    id = collection.insert(document)
    msg = "Inserted a new document for apk: #{document["n"]}, document id = #{id}"
    if(@verbose)
      puts msg
    end
    Logging.logger.info(msg)
  end

  def insert_document_if_not_exists(collection, document)
    apk = document['n']
    date_published = document['dtp']
    query = "{'n' => '#{apk}', 'dtp' => '#{date_published}'}"
    cursor = collection.find(eval(query))
    if !cursor.has_next?
      id = collection.insert(document)
      msg = "Inserted a new document for apk: #{apk}, date published: #{date_published}, document id = #{id}"
      if(@verbose)
        puts msg
      end
      Logging.logger.info(msg)
    else
      Logging.logger.info("Document already exists for apk: #{apk}, date published: #{date_published}")
    end
  end

  def document_reader(cmd, collection, json_file)
    json_reader = JsonReader.new
    Logging.logger.info("processing #{json_file}")
    app_info = json_reader.parse_json_data(json_file)
    if !app_info.nil?
      if(cmd.eql? "InsertIfNotExists")
        insert_document_if_not_exists(collection, app_info)
      elsif(cmd.eql? "InsertWithDuplicates")
        insert_document_with_duplicates(collection, app_info)
      end
    end
  end
  
  def start_main(cmd, source)
    beginning_time = Time.now
    if(!File.exist? source)
      puts "Error: No such file or directory"
      abort(@@usage)
    elsif(File.directory?(source))
      Logging.logger.info("Searching for .json files at #{source}")
      json_files = FilesFinder.new(source, '.json').find_files(@verbose)
      if(json_files.nil?)
        puts "The specified directory does not contain .json file(s)."
        abort(@@usage)
      end
      collection = connect_mongodb
      # If the source is a directory that contains json file(s).
      json_files.each do |json_file|
        document_reader(cmd, collection, json_file)
      end
     # If the source is a json file
    elsif (File.extname(source).downcase.eql? ".json")
      collection = connect_mongodb
      document_reader(cmd, collection, source)
    else
      abort(@@usage)
    end
    end_time = Time.now
    elapsed_seconds = end_time - beginning_time
    puts "Finished after #{Time.at(elapsed_seconds).utc.strftime("%H:%M:%S")}"
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
        opts.on('-l','--log <log_file,[level]>', Array, 'Write logs to the specified file with the given logging level such as error or info. The default logging level is info.') do |log_options|
	  log_level = 'info'
	  if(!log_options[1].nil?)
	    log_level = log_options[1]
	  end
	  config = {"dev" => log_options[0], "level" => log_level}
	  Logging.config_log(config)
        end
        opts.on('-H','--host <host_name>', 'The host name that the mongod is connected to. Default value is localhost.') do |host_name|
          @host = host_name
        end
        opts.on('-p','--port <port>', 'The port number that the mongod instance is listening. Default port number value is 27017.') do |port_num|
          @port = port_num
        end
	opts.on('-v', '--verbose', 'Causes the tool to be verbose to explain what is being done, showing .json files as they are processed.') do
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

    cmd = ""
    if(args[0].nil?)
      puts "Error command is not specified."
      abort(@@usage)
    else
        if(args[0].eql? "InsertWithDuplicates")
          cmd = "InsertWithDuplicates"
        elsif(args[0].eql? "InsertIfNotExists")
          cmd = "InsertIfNotExists"
        else
          puts "Unknown command. Valid commands are: InsertWithDuplicates or InsertIfNotExists."
          abort(@@usage)
        end
    end
    
    if(args[1].nil?)
      puts "Error source is not specified."
      abort(@@usage)
    end
    
    source = File.absolute_path(args[1])
    start_main(cmd, source)
  end
end

if __FILE__ == $PROGRAM_NAME
  main_obj = PublicMain.new
  main_obj.command_line(ARGV)
end
