#!/usr/bin/env ruby

require 'mongo'
require 'optparse'
require 'whatlanguage'
require_relative '../utils/logging'

class MongodbDriver

  @@usage = "Usage: #{$PROGRAM_NAME} {find_apps_with_permissions | find_apps_by_permission | find_top_apps} {out_dir} [OPTIONS]"
  DB_NAME = "apps"
  COLLECTION_NAME = "public"
  @collection
  @out_dir
  @per_name
  @limit
  
  attr_reader :host, :port
  
  def initialize
    @host = "localhost"
    @port = 27017
    @limit = 500
  end
  
  private
  def connect_mongodb
    mongo_client = Mongo::Connection.new(@host, @port)
    db = mongo_client.db(DB_NAME)
    @collection = db.collection(COLLECTION_NAME)
    Logging.logger.info("Connected to database #{DB_NAME}, collection #{COLLECTION_NAME}")
    @collection
  end

  def find_apps_with_permissions
    @collection.find({"per" => {"$not" => {"$size" => 0} } }, :fields => ["n", "desc", "per"]).each do |doc|
      name = doc["n"]
      desc = doc["desc"]
      next unless desc.language.to_s.eql? "english" || desc.split.size > 10
      out_file = File.join(@out_dir, name + ".raw.txt")
      File.open(out_file, 'w') { |file| file.write(desc) }
      Logging.logger.info("The app's description has been written to: #{out_file}")
    end
  end

  def find_apps_by_permission
    @collection.find({"per" => @per_name }, :fields => ["n", "desc", "per"]).each do |doc|
      name = doc["n"]
      desc = doc["desc"]
      next unless desc.language.to_s.eql? "english" || desc.split.size > 10
      out_file = File.join(@out_dir, name + ".raw.txt")
      File.open(out_file, 'w') { |file| file.write(desc) }
      Logging.logger.info("The app's description has been written to: #{out_file}")
    end
  end
  
  def find_top_apps
    name_hd = "apk_name"
    download_hd = "download_count"
    out_file = File.join(@out_dir, "top_apps.txt")
    File.open(name_hd, 'w') do |file| 
      file.write(name + ", " + download_hd)
      @collection.find({ "per" => { "$not" => { "$size" => 0 } } }, :fields => ["n", "dct"], :sort => ['dct', Mongo::DESCENDING], :limit => @limit).each do |doc|
        name = doc["n"]
        dct = doc["dct"]
        file.write(name + ", " + dct)
      end
    end
      Logging.logger.info("The top apps list has been written to: #{out_file}")
  end

  def start_main(out_dir, cmd)
    beginning_time = Time.now
    if(!File.directory?(out_dir))
      puts "No such directory."
      abort(@@usage)
    end
    @out_dir = out_dir
    connect_mongodb
    
    if(cmd.eql? "find_apps_by_permission")
      if(@per_name.nil?)
        puts "Please indicate the permission name using the option -P."
        abort(@@usage)
      else
        find_apps_with_permissions
      end
    elsif(cmd.eql? "find_apps_with_permissions")
      find_apps_with_permissions
    elsif(cmd.eql? "find_top_apps")
      find_top_apps
    end

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
        opts.on('-P','--permission <name>', 'One valid Android permission name that the application needs.') do |per_name|
          @per_name = per_name
        end
        opts.on('-l','--limit <value>', 'The number of documents in the result set.') do |limit_value|
          @limit = limit
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
    cmd = ""
    
    if(args[0].nil)
      abort(@@usage)
    end
    
    if(args[0].eql? "find_top_apps")
      cmd = "find_top_apps"
    elsif(args[0].eql? "find_apps_by_permission")
      cmd = "find_apps_by_permission"
    elsif(args[0].eql? "find_apps_with_permissions")
      cmd = "find_apps_with_permissions"
    else
      puts "Error: Unknown command."
      abort(@@usage)
    end
      
    if(args[1].nil?)
      abort(@@usage)
    else
      out_dir = File.absolute_path(args[0])
      start_main(out_dir, cmd)
    end
  end
end

if __FILE__ == $PROGRAM_NAME
  driver_obj = MongodbDriver.new
  driver_obj.command_line(ARGV)
end
