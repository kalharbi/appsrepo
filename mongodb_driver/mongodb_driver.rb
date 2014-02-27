#!/usr/bin/env ruby

require 'mongo'
require 'optparse'
require 'whatlanguage'
require_relative '../utils/logging'

class MongodbDriver

  @@usage = "Usage: #{$PROGRAM_NAME} {out_dir} [OPTIONS]"
  DB_NAME = "apps"
  COLLECTION_NAME = "public"
  @collection
  @out_dir
  attr_reader :host, :port
  
  def initialize
    @host = "localhost"
    @port = 27017
  end
  
  private
  def connect_mongodb
    mongo_client = Mongo::Connection.new(@host, @port)
    db = mongo_client.db(DB_NAME)
    @collection = db.collection(COLLECTION_NAME)
    Logging.logger.info("Connected to database #{DB_NAME}, collection #{COLLECTION_NAME}")
    @collection
  end

  def find_apps_by_permissions
    @collection.find({"per" => {"$not" => {"$size" => 0} } }, :fields => ["n", "desc", "per"]).each do |doc|
      name = doc["n"]
      desc = doc["desc"]
      next unless desc.language.to_s.eql? "english" || desc.split.size > 10
      out_file = File.join(@out_dir, name + ".raw.txt")
      File.open(out_file, 'w') { |file| file.write(desc) }
      Logging.logger.info("The app's description has been written to: #{out_file}")
    end
  end

  def start_main(out_dir)
    beginning_time = Time.now
    if(!File.directory?(out_dir))
      puts "No such directory."
      abort(@@usage)
    end
    @out_dir = out_dir

    connect_mongodb
    find_apps_by_permissions

    end_time = Time.now
    elapsed_time = end_time - beginning_time
    Logging.logger.info("Finished after #{Time.at(elapsed_time).utc.strftime("%H:%M:%S")}")
  end

  public
  def command_line(args)
    begin
      opt_parser = OptionParser.new do |opts|
        opts.banner = @@usage
        opts.on('-h','--help', 'Show this help message and exit') do
          puts opts
          exit
        end
        opts.on('-l','--log <log_file,[level]>', Array, 'Write logs to the specified file with the given lo    gging level such as error or info. The default logging level is info.') do |log_options|
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
        opts.on('-v', '--verbose', 'Causes the tool to be verbose to explain what is being done.') do
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
      out_dir = File.absolute_path(args[0])
      start_main(out_dir)
    end
  end
end

if __FILE__ == $PROGRAM_NAME
  driver_obj = MongodbDriver.new
  driver_obj.command_line(ARGV)
end
