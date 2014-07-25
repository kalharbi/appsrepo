#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require 'mongo'
require 'optparse'
require_relative '../utils/log'
require_relative 'files_finder'
require_relative 'aapt_executor'

class UpdateFields
  
  @@log = Log.instance
  @@usage = "Usage: #{$PROGRAM_NAME} {UpdateTitleAndDeveloper} {json_file | json_directory} [OPTIONS]"
  DB_NAME = "apps"
  COLLECTION_NAME = "public"
  attr_reader :host, :port
  attr_accessor :update_count

  def initialize
    @host = "localhost"
    @port = 27017
    @update_count = 0
  end
  
  private
  def connect_mongodb
    mongo_client = Mongo::Connection.new(@host, @port)
    db = mongo_client.db(DB_NAME)
    collection = db.collection(COLLECTION_NAME)
    @@log.info("Connected to database: #{DB_NAME}, collection: #{COLLECTION_NAME}")
    collection
  end
  
  # Update the title and developer for the given document.
  def update_title_and_developer(collection, document, title, developer)
    package_name = document['n']
    version_code = document['verc']
    id = document['_id']
    selector_query = "{'_id' => BSON::ObjectId('#{id}')}"
    updated_fields = '{"$set" => {"t" => "#{title}", "crt" => "#{developer}"} }'
    response = collection.update(eval(selector_query), eval(updated_fields))
    if response['updatedExisting'] == true
      @update_count += 1
      @@log.info("Successfully updated the document for package name: #{package_name}, version code: #{version_code}")
    else
      @@log.error("Failed to update document #{id} for package name: #{package_name}, version code: #{version_code}. Error: #{response.to_s}")
    end
  end
  
  # Returns a MongoDB document of the stored app public features.
  def get_app_document(collection, package_name, version_code)
    query = "{'n' => '#{package_name}', 'verc' => '#{version_code}'}"
    return collection.find_one(eval(query))
  end
  
  def document_reader(cmd, collection, json_file)
    # Get package name from file name
    file_name = File.basename(json_file,".json")
    package_name = remove_download_date_from_apk_name(file_name)
    @@log.info("processing JSON file: #{json_file}")
    f = nil
    data = nil
    begin
      f = File.read(json_file)
      data = JSON.parse(f)
      return if data.nil?
    rescue Exception => e
      @@log.error("Error in JSON file: #{json_file} - #{e.message}")
      return
    end
    # Get version name and version code info from aapt tool
    version_info = get_version_info(File.join(File.dirname(json_file), File.basename(json_file, ".json") + ".apk"))
    return if version_info.length == 0
    version_code = version_info[:version_code]
    title = data['title']
    developer = data['creator']
    price = data['price']
    # Return if it's a paid app
    return if price.start_with? '$'
    # check if the JSON document exists in the database
    doc = get_app_document(collection, package_name, version_code)
    if !doc.nil?
      db_title = doc['t']
      db_developer = doc['crt']
      if db_title.eql? title and db_developer.eql? developer
        @@log.info("App title and developer info is consistent with the database.")
        return
      else
        @@log.info("App title and developer info is not consistent with the database for package name: #{package_name}, version code: #{version_code}. Updating the database...")
        update_title_and_developer(collection, doc, title, developer)
      end
    else
      Logging.logger.warn("App does does not exist in the database (package name: #{package_name}, version code: #{version_code})")
    end
  end
  
  # Get version name and version code using aapt from the apk file
  def get_version_info(apk_file)
    version_info = Hash.new
    if(File.exist? apk_file)
      @@log.info("Running aapt on APK file: #{apk_file}")
      aapt_executor = AaptExecutor.new(apk_file)
      version_info = aapt_executor.get_version_info
    else
      @@log.error("APK file does not exist. #{apk_file}")
    end
    version_info
  end
  
  # Remove the download date from the apk name.
  def remove_download_date_from_apk_name(apk_name)
    date_index = apk_name.rindex('.201')
    if !date_index.nil?
      if is_number?(apk_name[-8..-1])
        apk_name = apk_name[0..-10]
      end
    end
    apk_name
  end
  
  def is_number?(number)
    true if Float(number) rescue false
  end
  
  def start_main(cmd, source)
    beginning_time = Time.now
    if(!File.exist? source)
      puts "Error: No such file or directory"
      abort(@@usage)
    elsif(File.directory?(source))
      @@log.info("Searching for .json files at #{source}")
      json_files = FilesFinder.new(source, '.json').find_files(true)
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
    puts "#@update_count records have been updated"
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
        opts.on('-H','--host <host_name>', 'The host name that the mongod is connected to. Default value is localhost.') do |host_name|
          @host = host_name
        end
        opts.on('-p','--port <port>', 'The port number that the mongod instance is listening. The Default port number is 27017.') do |port_num|
          @port = port_num
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
    end
    
    if(args[0].eql? "UpdateTitleAndDeveloper")
      cmd = "UpdateTitleAndDeveloper"
    else
      puts "Unknown command. Valid command is: UpdateTitleAndDeveloper."
      abort(@@usage)
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
  # Load configurations
  Settings.load('./config/public_features.conf')
  main_obj = UpdateFields.new
  main_obj.command_line(ARGV)
end
