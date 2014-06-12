#!/usr/bin/env ruby

require 'mongo'
require 'optparse'
require 'whatlanguage'
require 'time'
require_relative '../utils/logging'

class MongodbDriver

  @@usage = "Usage: ruby #{$PROGRAM_NAME} <command> <out_dir> [OPTIONS]"
  @@cmd_desc = "\n\nThe following commands are available:\n\n"+
               "    find_apps_by_permission -P <permission_name> \n    find_top_apps\n    find_bottom_apps  \n" + 
               "    find_top_bottom_apps_in_any_permission -P <comma_separated_permission_names>\n" +
               "    find_top_bottom_apps_not_in_any_permission -P <comma_separated_permission_names>\n" +
               "    write_description_for_all_apps_with_at_least_one_permission\n" +
               "    write_apps_description_by_permission -P <permission_name>\n" +
               "    write_apps_description_by_package_name -k <file_names_of_packages>" + 
               "\n\n The following options are available:\n\n"
    
  DB_NAME = "apps"
  COLLECTION_NAME = "public"
  @db
  @collection
  @out_dir
  @package_names_file
  @per_name
  @per_list = []
  @limit
  @price
  attr_reader :host, :port, :limit, :price
  
  def initialize
    @host = "localhost"
    @port = 27017
    @limit = 500
  end
  
  private
  def connect_mongodb
    mongo_client = Mongo::Connection.new(@host, @port)
    @db = mongo_client.db(DB_NAME)
    @collection = @db.collection(COLLECTION_NAME)
    Logging.logger.info("Connected to database #{DB_NAME}, collection #{COLLECTION_NAME}")
    @collection
  end

  # Find apps by permission and price. Write their names to a file in the target directory
  def find_apps_by_permission
    query = "{'per' => '#@per_name'}"
    opts = "{:fields => ['n']}"
    out_file_name = "#@per_name-all_apps.txt"
    if(!@price.nil?)
      if(@price.casecmp("free") == 0)
        query = "{'per' => '#@per_name', 'pri' => 'Free' }"
        out_file_name = "#@per_name-free_apps.txt"
      elsif(@price.casecmp("paid") == 0)
        query = "{'per' => '#@per_name', 'pri' => {'$ne' => 'Free'}}"        
        out_file_name = "#@per_name-paid_apps.txt"
      end
    end
    out_file = File.join(@out_dir, out_file_name)
    File.open(out_file, 'w') do |file| 
      @collection.find(eval(query), eval(opts) ).each do |doc|
        name = doc["n"]
        file.puts(name)
        Logging.logger.info(name)
      end
    end
    Logging.logger.info("The apps list has been written to: #{out_file}")
  end
  
  # Find apps that have at least one permission and write the description if it's English
  def write_description_for_all_apps_with_at_least_one_permission
    query = "{'per' => {'$not' => {'$size' => 0} } }"
    opts = "{:fields => ['n', 'desc', 'per']}"
    if(!@price.nil?)
      if(@price.casecmp("free") == 0)
        query = "{'per' => {'$not' => {'$size' => 0} }, 'pri' => 'Free' }"
      elsif(@price.casecmp("paid") == 0)
        query = "{'per' => {'$not' => {'$size' => 0} }, 'pri' => {'$ne' => 'Free'} }"
      end
    end
    @collection.find(eval(query), eval(opts)).each do |doc|
      name = doc["n"]
      desc = doc["desc"]
      next unless desc.language.to_s.eql? "english" || desc.split.size > 10
      out_file = File.join(@out_dir, name + ".raw.txt")
      File.open(out_file, 'w') { |file| file.write(desc) }
      Logging.logger.info("The app's description has been written to: #{out_file}")
    end
  end
  
  # Find apps by permission and write the description if it's English
  def write_apps_description_by_permission
    query = "{'per' => '#@per_name' }"
    opts = "{:fields => ['n', 'desc', 'per']}"
    if(!@price.nil?)
      if(@price.casecmp("free") == 0)
       query = "{'per' => '#@per_name', 'pri' => 'Free' }"
      elsif(@price.casecmp("paid") == 0)
        query = "{'per' => '#@per_name', 'pri' => {'$ne' => 'Free'} }"
      end
    end
    @collection.find(eval(query), eval(opts)).each do |doc|
      name = doc["n"]
      desc = doc["desc"]
      next unless desc.language.to_s.eql? "english" || desc.split.size > 10
      out_file = File.join(@out_dir, name + ".raw.txt")
      File.open(out_file, 'w') { |file| file.write(desc) }
      Logging.logger.info("The app's description has been written to: #{out_file}")
    end
  end
  
  # Find apps by apk name and write their description if it's English
  def write_apps_description_by_package_name
    opts = "{:fields => ['n', 'desc', 'ver']}"
    File.open(@package_names_file, 'r').each_with_index do |line, index|
      next if index == 0 #skips first line that contains the header info (apk_name, download_count)
      package_name = line.split(',')[0]
      query = "{'n' => '#{package_name}'}"
      @collection.find(eval(query), eval(opts)).each do |doc|
        name = doc["n"]
        desc = doc["desc"]
        ver = doc["ver"]
        out_file = File.join(@out_dir, name + ".description.txt")
        File.open(out_file, 'w') { |result_file| result_file.write(desc) }
        Logging.logger.info("The app's description has been written to: #{out_file}")
      end
    end
  end
  
  # Run mapreduce to find unique top/bottom apps that use any of the given permissions.
  # That's it, find top and bottom downloaded apps that use any of the specified permissions.
  def find_top_bottom_apps_in_any_permission
    collection_name = nil
    file_name = nil
    query = nil
    
    # Prepare the collection that will be passed to the mapreduce function.
    # The goal is to limit the mapreduce operation to a subset of the collection.
    if(!@per_list.nil?)
      per_values = @per_list.join(',') # combine the permissions in a single comma separated string.
      file_name_per_part = '-'
      # set the result collection name
      map = {' ' => '', '-' => '_', ':' => '_'}
      regex = Regexp.new(map.keys.map { |x| Regexp.escape(x) }.join('|'))
      collection_name = 'in_' + @per_list[0].split('.')[-1] + '_'+ Time.now.to_s.gsub(regex, map)
      @per_list.each do |p|
        file_name_per_part << p.split('.')[-1] + '-'
      end
      if(!@price.nil? and @price.casecmp("free") == 0)
        query = "{ 'pri' => 'Free', 'per' => { '$in' => #@per_list } }"
        file_name = "free" + "#{file_name_per_part}" + "apps.txt"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'per' => { $in: '#@per_list' } }"
        file_name = "paid" + "#{file_name_per_part}" + "apps.txt"
      else
        query = "{'per' => { $in: '#@per_list' } }"
        file_name = "#{file_name_per_part}" + "apps.txt"
      end
    else
      Logging.logger.error("Permission list is empty.")
      return
    end
    
    # Phase 1: Perform map-reduce and output to a collection named collection_name
    # MapReduce Options Hash. 
    opts = "{ :query => #{query}, :out => '#{collection_name}' }"
    # map and reduces functions written in JavaScript
    map = 'function(){emit( {apk_name: this.n, download: this.dct}, {count: 1});};'
    reduce = 'function(key, values){ return 1; };'
    # Perform map-reduce operation on the public collection.
    @collection.map_reduce(map, reduce, eval(opts))
    
    custom_collection = @db.collection(collection_name)
    
    # Phase2: Query the output collection
    top_file_name = 'top_either_' + file_name
    bottom_file_name = 'bottom_either_' + file_name
    opts_for_top = nil
    opt_for_bottom = nil
    if(!@limit.nil?)
      opts_for_top = "{ :sort => [['_id.download', Mongo::DESCENDING]], :limit => #@limit}"
      opt_for_bottom ="{ :sort => [['_id.download', Mongo::ASCENDING]], :limit => #@limit}"
    else
      opts_for_top = "{ :sort => [['_id.download', Mongo::DESCENDING]]}"
      opt_for_bottom ="{ :sort => [['_id.download', Mongo::ASCENDING]]}"
    end
    # write the results into two files
    #1) Write the results of top apps.
    name_hd = "apk_name, download_count"
    top_out_file = File.join(@out_dir, top_file_name)
    File.open(top_out_file, 'w') do |file|
      file.puts(name_hd)
      custom_collection.find(Hash.new(0), eval(opts_for_top)).each do |doc|
        name = doc['_id']['apk_name']
        dct = doc['_id']['download']
        line = name + ", " + dct.to_s
        Logging.logger.info(line)
        file.puts(line)
      end
    end
    #2) Write the results of bottom apps.
    bottom_out_file = File.join(@out_dir, bottom_file_name)
    File.open(bottom_out_file, 'w') do |file|
      file.puts(name_hd)
      custom_collection.find(Hash.new(0), eval(opt_for_bottom)).each do |doc|
        name = doc['_id']['apk_name']
        dct = doc['_id']['download']
        line = name + ", " + dct.to_s
        Logging.logger.info(line)
        file.puts(line)
      end
    end
    Logging.logger.info("The top apps list has been written to: #{top_out_file}")
    Logging.logger.info("The bottom apps list has been written to: #{bottom_out_file}")          
    
  end
  
  # Run mapreduce to find unique top/bottom apps that use neither of the given permissions.
  # That's it, find top and bottom downloaded apps that do not use any of the specified permissions.
  def find_top_bottom_apps_not_in_any_permission
    collection_name = nil
    file_name = nil
    query = nil
    
    # Prepare the collection that will be passed to the mapreduce function.
    # The goal is to limit the mapreduce operation to a subset of the collection.
    if(!@per_list.nil?)
      per_values = @per_list.join(',') # combine the permissions in a single comma separated string.
      file_name_per_part = '-'
      # set the result collection name
      map = {' ' => '', '-' => '_', ':' => '_'}
      regex = Regexp.new(map.keys.map { |x| Regexp.escape(x) }.join('|'))
      collection_name = 'not_in_' + @per_list[0].split('.')[-1] + '_'+ Time.now.to_s.gsub(regex, map)
      @per_list.each do |p|
        file_name_per_part << p.split('.')[-1] + '-'
      end
      if(!@price.nil? and @price.casecmp("free") == 0)
        query = "{ 'pri' => 'Free', 'per' => { '$nin' => #@per_list } }"
        file_name = "free" + "#{file_name_per_part}" + "apps.txt"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'per' => { $nin: '#@per_list' } }"
        file_name = "paid" + "#{file_name_per_part}" + "apps.txt"
      else
        query = "{'per' => { $nin: '#@per_list' } }"
        file_name = "#{file_name_per_part}" + "apps.txt"
      end
    else
      Logging.logger.error("Permission list is empty.")
      return
    end
    
    # Phase 1: Perform map-reduce and output to a collection named collection_name
    # MapReduce Options Hash. 
    opts = "{ :query => #{query}, :out => '#{collection_name}' }"
    # map and reduces functions written in JavaScript
    map = 'function(){emit( {apk_name: this.n, download: this.dct}, {count: 1});};'
    reduce = 'function(key, values){ return 1; };'
    # Perform map-reduce operation on the public collection.
    @collection.map_reduce(map, reduce, eval(opts))
    
    custom_collection = @db.collection(collection_name)
    
    # Phase2: Query the output collection
    top_file_name = 'top_neither_' + file_name
    bottom_file_name = 'bottom_neither_' + file_name
    opts_for_top = nil
    opt_for_bottom = nil
    if(!@limit.nil?)
      opts_for_top = "{ :sort => [['_id.download', Mongo::DESCENDING]], :limit => #@limit}"
      opt_for_bottom ="{ :sort => [['_id.download', Mongo::ASCENDING]], :limit => #@limit}"
    else
      opts_for_top = "{ :sort => [['_id.download', Mongo::DESCENDING]]}"
      opt_for_bottom ="{ :sort => [['_id.download', Mongo::ASCENDING]]}"
    end
    # write the results into two files
    #1) Write the results of top apps.
    name_hd = "apk_name, download_count"
    top_out_file = File.join(@out_dir, top_file_name)
    File.open(top_out_file, 'w') do |file|
      file.puts(name_hd)
      custom_collection.find(Hash.new(0), eval(opts_for_top)).each do |doc|
        name = doc['_id']['apk_name']
        dct = doc['_id']['download']
        line = name + ", " + dct.to_s
        Logging.logger.info(line)
        file.puts(line)
      end
    end
    #2) Write the results of bottom apps.
    bottom_out_file = File.join(@out_dir, bottom_file_name)
    File.open(bottom_out_file, 'w') do |file|
      file.puts(name_hd)
      custom_collection.find(Hash.new(0), eval(opt_for_bottom)).each do |doc|
        name = doc['_id']['apk_name']
        dct = doc['_id']['download']
        line = name + ", " + dct.to_s
        Logging.logger.info(line)
        file.puts(line)
      end
    end
    Logging.logger.info("The top apps list has been written to: #{top_out_file}")
    Logging.logger.info("The bottom apps list has been written to: #{bottom_out_file}")    
  end
  
  def find_top_apps
    query = "{}"
    opts = "{ :fields => ['n', 'dct'], :sort => [['dct', Mongo::DESCENDING]], :limit => #@limit}"
    file_name = "top_apps.txt"
    if(!@price.nil?)
       if(@price.casecmp("free") == 0)
         query = "{ 'pri' => 'Free' }"
         file_name = "top_free_apps.txt"
       elsif(@price.casecmp("paid") == 0)
         query = "{ 'pri' => {'$ne' => 'Free'} }"
         file_name = "top_paid_apps.txt"
       end
    end
    if(!@per_name.nil?)
      if(!@price.nil? and @price.casecmp("free") == 0)
        query = "{ 'pri' => 'Free', 'per' => '#@per_name' }"
        file_name_per_part = @per_name.split('.')[-1]
        file_name = "top_free_" + "#{file_name_per_part}" + "_apps.txt"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'per' => '#@per_name' }"
        file_name = "top_paid_" + "#@per_name.split('.')[-1]" + "_apps.txt"
      else
        query = "{'per' => '#@per_name' }"
        file_name = "top_" + "#@per_name.split('.')[-1]" + "_apps.txt"
      end
    end
    
    name_hd = "apk_name"
    download_hd = "download_count"
    out_file = File.join(@out_dir, file_name)
    File.open(out_file, 'w') do |file|
      file.puts(name_hd + ", " + download_hd)
      @collection.find(eval(query), eval(opts)).each do |doc|
        name = doc['n']
        dct = doc["dct"]
        line = name + ", " + dct.to_s
        Logging.logger.info(line)
        file.puts(line)
      end
    end
      Logging.logger.info("The top apps list has been written to: #{out_file}")
  end

  def find_bottom_apps
    query = "{}"
    opts = "{ :fields => ['n', 'dct'], :sort => [['dct', Mongo::ASCENDING]], :limit => #@limit}"
    file_name = "bottom_apps.txt"
    if(!@price.nil?)
       if(@price.casecmp("free") == 0)
         query = "{ 'pri' => 'Free' }"
         file_name = "bottom_free_apps.txt"
       elsif(@price.casecmp("paid") == 0)
         query = "{ 'pri' => {'$ne' => 'Free'} }"
         file_name = "bottom_paid_apps.txt"
       end
    end
    if(!@per_name.nil?)
      if(!@price.nil? and @price.casecmp("free") == 0)
        query = "{ 'pri' => 'Free', 'per' => '#@per_name' }"
        file_name_per_part = @per_name.split('.')[-1]
        file_name = "bottom_free-" + "#{file_name_per_part}" + "-apps.txt"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'per' => '#@per_name' }"
        file_name = "bottom_paid-" + "#@per_name.split('.')[-1]" + "-apps.txt"
      else
        query = "{'per' => '#@per_name' }"
        file_name = "bottom-" + "#@per_name.split('.')[-1]" + "-apps.txt"
      end
    end
          
    name_hd = "apk_name"
    version_hd = "version"
    download_hd = "download_count"
    
    out_file = File.join(@out_dir, file_name)
    File.open(out_file, 'w') do |file|
      file.puts(name_hd + ", " + download_hd)
      @collection.find(eval(query), eval(opts)).each do |doc|
        name = doc["n"]
        ver = doc["ver"]
        dct = doc["dct"]
        line = name + ", " + dct.to_s
        Logging.logger.info(line)
        file.puts(line)
      end
    end
      Logging.logger.info("The bottom apps list has been written to: #{out_file}")
  end

  def start_main(out_dir, cmd)
    beginning_time = Time.now
    if(!File.directory?(out_dir))
      puts "No such directory. #{out_dir}"
      abort(@@usage)
    end
    @out_dir = out_dir
    connect_mongodb
    if(!@price.nil?)
      if(!(@price.casecmp("free") == 0  || @price.casecmp("paid") == 0))
        puts "Error: Unknown fee value. Please user either free or paid"
      end
    end
    
    # Check command name
    if(cmd.eql? "find_apps_by_permission")
      if(@per_name.nil?)
        puts "Please indicate the permission name using the option -P."
        abort(@@usage)
      else
        find_apps_by_permission
      end
    elsif(cmd.eql? "find_top_apps")
      find_top_apps
    elsif(cmd.eql? "find_bottom_apps")
      find_bottom_apps
    elsif(cmd.eql? "find_top_bottom_apps_in_any_permission")
      if(@per_list.nil?)
        puts "Please use the -P option to specify the permissions in a comma-separated list."
        abort(@@usage)
      else
        find_top_bottom_apps_in_any_permission
      end
    elsif(cmd.eql? "find_top_bottom_apps_not_in_any_permission")
      if(@per_list.nil?)
        if(@per_name.nil?)
          puts "Please use the -P option to specify a permission or a set of permissions in a comma-separated values format."
          abort(@@usage)
        else
          @per_list = [@per_name]
        end
      end
      find_top_bottom_apps_not_in_any_permission
    elsif(cmd.eql? "write_apps_description_by_permission")
      if(@per_name.nil?)
        puts "Please indicate the permission name using the option -P."
        abort(@@usage)
      else
        write_apps_description_by_permission
      end
    elsif(cmd.eql? "write_description_for_all_apps_with_at_least_one_permission")
      write_description_for_all_apps_with_at_least_one_permission
    elsif(cmd.eql? "write_apps_description_by_package_name")
      if(@package_names_file.nil?)
        puts "Error: Please use the -k option to specify the package names file."
        abort(@@usage)
      elsif File.file?(@package_names_file)
        write_apps_description_by_package_name
      else
        puts "Error: package names file #{@package_names_file} does not exist."
        exit
      end
    end
    
    end_time = Time.now
    elapsed_time = end_time - beginning_time
    Logging.logger.info("Finished after #{Time.at(elapsed_time).utc.strftime("%H:%M:%S")}")
  end

  public
  def command_line(args)
    begin
      opt_parser = OptionParser.new do |opts|
        opts.banner = @@usage + @@cmd_desc
        opts.on('-h','--help', 'Show this help message and exit') do
          puts opts
          exit
        end
        opts.on('-l','--log <log_file,[level]>', Array, 'Write logs to the specified file with the given logging level', 'such as error or info. The default logging level is info.') do |log_options|
          log_level = 'info'
          if(!log_options[1].nil?)
            log_level = log_options[1]
          end
          config = {"dev" => log_options[0], "level" => log_level}
          Logging.config_log(config)
        end
        opts.on('-H','--host <host_name>', 'The host name that the mongod is connected to. Default value', 'is localhost.') do |host_name|
          @host = host_name
        end
        opts.on('-p','--port <port>', 'The port number that the mongod instance is listening. Default port ', 'number value is 27017.') do |port_num|
          @port = port_num
        end
        opts.on('-P','--permission <name>', 'One valid Android permission name that the application uses,or a', 'list of comma separated permissions that the app may use (inclusive disjunction).') do |per_name|
          if(per_name.include? ',')
            @per_list = per_name.split(',')
          else
            @per_name = per_name
          end
        end
        opts.on('-k','--package <pckg_list_file>', 'File that contains a list of package names.') do |package_names_file|
          @package_names_file = package_names_file
        end
        opts.on('-f', '--fee <Free|Paid>', 'The fee to indicate whether to return free or paid apps.', 'Valid values are free or paid') do |fee_value|
          @price = fee_value
        end
        opts.on('-m','--max <value>', 'The maximum number of documents to return.') do |max_value|
          @limit = max_value
        end
        opts.on('-v', '--verbose', 'Causes the tool to be verbose to explain what is being done.') do
          @verbose = true
        end
      end
      opt_parser.parse!
    rescue OptionParser::AmbiguousArgument
      puts "Error: illegal command line argument.\n"
      puts opt_parser.help()
      exit
    rescue OptionParser::InvalidOption
      puts "Error: illegal command line option.\n"
      puts opt_parser.help()
      exit
    rescue OptionParser::MissingArgument
      puts "Error: missing argument.\n"
      puts opt_parser.help()
      exit
    end
    cmd = ""
    
    if(args[0].nil?)
      puts 'Error: command is missing.'
      abort(@@usage)
    end
    
    if(args[0].eql? "find_apps_by_permission")
      cmd = "find_apps_by_permission"
    elsif(args[0].eql? "find_top_apps")
      cmd = "find_top_apps"
    elsif(args[0].eql? "find_bottom_apps")
      cmd = "find_bottom_apps"
    elsif(args[0].eql? "find_top_bottom_apps_in_any_permission")
      cmd = "find_top_bottom_apps_in_any_permission"
    elsif(args[0].eql? "find_top_bottom_apps_not_in_any_permission")
      cmd = "find_top_bottom_apps_not_in_any_permission"
    elsif(args[0].eql? "write_apps_description_by_permission")
      cmd = "write_apps_description_by_permission"
    elsif(args[0].eql? "write_apps_description_by_package_name")
      cmd = "write_apps_description_by_package_name"
    elsif(args[0].eql? "write_description_for_all_apps_with_at_least_one_permission")
      cmd = "write_description_for_all_apps_with_at_least_one_permission"
    else
      puts "Error: Unknown command."
      abort(@@usage)
    end
    
    if(args[1].nil?)
      puts("Results output direcotry is missing.")
      abort(@@usage)
    else
      out_dir = File.absolute_path(args[1])
      start_main(out_dir, cmd)
    end
  end
end


if __FILE__ == $PROGRAM_NAME
  driver_obj = MongodbDriver.new
  driver_obj.command_line(ARGV)
end

