#!/usr/bin/env ruby

require 'mongo'
require 'optparse'
require 'whatlanguage'
require 'time'
require_relative '../utils/log'

class MongodbDriver
  
  @@log = nil
  @@usage = "Usage: ruby #{$PROGRAM_NAME} <command> <out_dir> [OPTIONS]"
  @@cmd_desc = "\n\nThe following commands are available:\n\n" +
               "    find_apps_by_permission -P <permission_name> \n    find_top_apps\n    find_bottom_apps  \n" + 
               "    find_top_bottom_apps_in_any_permission -P <comma_separated_permission_names>\n" +
               "    find_top_bottom_apps_not_in_any_permission -P <comma_separated_permission_names>\n" +
               "    write_description_for_all_apps_with_at_least_one_permission\n" +
               "    write_apps_description_by_permission -P <permission_name>\n" +
               "    write_apps_description_by_package_name -k <file_names_of_packages>\n" +
               "    write_apps_description\n" + 
               "    find_version_code -k <file_names_of_packages>\n" +
               "    find_app_info -k <file_names_of_packages_and_code_versions>\n" +
               "\n\n The following options are available:\n\n"
 
  @mongo_client
  @db
  @db_name
  @db_user
  @db_pw
  @db_collection_name
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
    @db_name = "apps"
    @db_collection_name = "public"
  end
  
  private
  def connect_mongodb
    @mongo_client = Mongo::MongoClient.new(@host, @port)
    @db = @mongo_client.db(@db_name)
    if(!@db_user.nil? and !@db_pw.nil?)
      @db.authenticate(@db_user, @db_pw)
    end
    @collection = @db.collection(@db_collection_name)
    @@log.info("Connected to database #{@db_name}, collection #{@db_collection_name}")
    @collection
  end
  
  # Close the connection to the database
  def close_mongodb_connection
    @mongo_client.close()
  end
  
  # Find apps by permission and price. Write their names to a file in the target directory
  def find_apps_by_permission
    query = "{'per' => '#@per_name'}"
    opts = "{:fields => ['n'], :timeout => false}"
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
        @@log.info(name)
      end
    end
    @@log.info("The apps list has been written to: #{out_file}")
  end
  
  # Find apps that have at least one permission and write the description if it's English
  def write_description_for_all_apps_with_at_least_one_permission
    query = "{'per' => {'$not' => {'$size' => 0} } }"
    opts = "{:fields => ['n', 'desc', 'per'], :timeout => false}"
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
      @@log.info("The app's description has been written to: #{out_file}")
    end
  end
  
  # Find apps that have at least one permission and write the description if it's English
  def write_description_for_all_apps_with_at_least_one_permission
    query = "{'per' => {'$not' => {'$size' => 0} } }"
    opts = "{:fields => ['n', 'desc', 'per'], :timeout => false}"
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
      @@log.info("The app's description has been written to: #{out_file}")
    end
  end
  
  # Write the description for all apps if it's English
  def write_apps_description
    puts "in write_apps_description..."
    query = "{}"
    opts = "{:fields => ['n', 'verc', 'desc'], :timeout => false}"
    if(!@limit.nil?)
      opts = "{:fields => ['n', 'verc', 'desc'], :timeout => false, :limit => #@limit}"
    end
    if(!@price.nil?)
      if(@price.casecmp("free") == 0)
       query = "{'pri' => 'Free' }"
      elsif(@price.casecmp("paid") == 0)
        query = "{'pri' => {'$ne' => 'Free'} }"
      end
    end
    @collection.find(eval(query), eval(opts)) do |cursor|
      cursor.each do |doc|
        name = doc["n"]
        verc = doc["verc"]
        # paid apps have no version code, so use ? mark
        if verc.nil?
          verc = '?'
        end
        desc = doc["desc"]
        next unless desc.language.to_s.eql? "english" || desc.split.size > 10
        out_file = File.join(@out_dir, name + "-" + verc.to_s + ".raw.txt")
        File.open(out_file, 'w') { |file| file.write(desc) }
        @@log.info("The app's description has been written to: #{out_file}")
      end
    end
  end
  
  # Find apps by apk name and write their description if it's English
  def write_apps_description_by_package_name
    opts = "{:fields => ['n', 'desc', 'verc'], :timeout => false}"
    File.open(@package_names_file, 'r').each_with_index do |line, index|
      next if index == 0 #skips first line that contains the header info (apk_name, download_count)
      items = line.split(',')
      package_name = items[0]
      version_code = items[1]
      query = "{'n' => '#{package_name}', 'verc' => '#{version_code}' }"
      @collection.find(eval(query), eval(opts)) do |cursor|
        cursor.each do |doc|
          name = doc["n"]
          desc = doc["desc"]
          verc = doc["verc"]
          out_file = File.join(@out_dir, name + "-" + verc + ".description.txt")
          File.open(out_file, 'w') { |result_file| result_file.write(desc) }
          @@log.info("The app's description has been written to: #{out_file}")
        end
      end
    end
  end
  
  # Find version code for a list of package names
  def find_version_code
    opts = "{:fields => ['n', 'verc', 'dct'], :timeout => false}"
    if(!@limit.nil?)
      opts = "{:fields => ['n', 'verc', 'dct'], :limit => #@limit, :timeout => false}"
    end
    
    result_arr = []
    File.open(@package_names_file, 'r').each_with_index do |line, index|
      next if index == 0 #skips first line that contains the header info (apk_name, download_count)
      package_name = line.split(',')[0]
      query = "{'n' => '#{package_name}'}"
      @collection.find(eval(query), eval(opts)) do |cursor|
        cursor.each do |doc|
          name = doc["n"]
          verc = doc["verc"]
          dct = doc["dct"]
          if(verc.nil?)
            @@log.error("Missing version code for package #{name}")
            next
          end
          line = name + "," + verc + "," + dct.to_s
          result_arr << line
        end
      end
    end
    # Write results to  file
    out_file = File.join(@out_dir, "version_code.csv")
    name_hd = "package_name,version_code,download_count"
    File.open(out_file, 'w') do |file|
      file.puts(name_hd)
      result_arr.each do |entry|
        file.puts(entry)
      end
    end
    @@log.info("Package names and version codes have been written to: #{out_file}")
  end
  
  # Find additional info for a list of package names and version code values
  def find_app_info
    opts = "{:fields => ['t', 'n', 'vern', 'cat', 'rate', 'dct', 'dtp', 'crt', 'per'], :timeout => false}"
    
    result_arr = []
    File.open(@package_names_file, 'r').each_with_index do |line, index|
      next if index == 0 #skips first line that contains the header info (apk_name, download_count)
      items = line.split(',')
      package_name = items[0]
      version_code = items[1]
      query = "{'n' => '#{package_name}', 'verc' => '#{version_code}' }"
      @collection.find(eval(query), eval(opts)) do |cursor|
        cursor.each do |doc|
          title = doc["t"]
          package_name = doc["n"]
          version_name = doc["vern"]
          category = doc["cat"]
          rating = doc["rate"]
          download_count = doc["dct"]
          date_published = doc["dtp"]
          developer = doc["crt"]
          permission_size = doc["per"].length
          line = title + "," + package_name + "," + version_name  + "," + category + "," + rating + 
                 "," + download_count.to_s + "," + date_published + "," + developer + "," + permission_size.to_s
          result_arr << line
        end
      end
    end
    # Write results to  file
    out_file = File.join(@out_dir, "additional_info.csv")
    name_hd = "title,package,version_name,category,rating,download,date_published,developer,permissions"
    File.open(out_file, 'w') do |file|
      file.puts(name_hd)
      result_arr.each do |entry|
        file.puts(entry)
      end
    end
    @@log.info("Apps additional info have been written to: #{out_file}")
  end
  
  # Find top/bottom apps that use any of the given permissions.
  def find_top_bottom_apps_in_any_permission
    collection_name = nil
    file_name = nil
    query = nil
    
    # Prepare the query to the collection.
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
        query = "{ 'pri' => 'Free', 'per' => { '$in' => #@per_list }, 'verc' => {'$ne' => nil} }"
        file_name = "free" + "#{file_name_per_part}" + "apps.csv"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'per' => { $in: '#@per_list' }}"
        file_name = "paid" + "#{file_name_per_part}" + "apps.csv"
      else
        query = "{'per' => { $in: '#@per_list' } }"
        file_name = "#{file_name_per_part}" + "apps.csv"
      end
    else
      @@log.error("Permission list is empty.")
      return
    end
    
    # Result files
    top_file_name = 'top_either_' + file_name
    bottom_file_name = 'bottom_either_' + file_name
    # Set the sort order for top/bottom results
    opts_for_top = "{ :sort => [['dct', Mongo::DESCENDING]], :timeout => false}"
    opt_for_bottom ="{ :sort => [['dct', Mongo::ASCENDING]], :timeout => false}"
    
    # write the results into two files
    #1) Write the results of top apps.
    count = 0
    top_package_names_list = []
    name_hd = "apk_name,version_code,download_count"
    top_out_file = File.join(@out_dir, top_file_name)
    File.open(top_out_file, 'w') do |file|
      file.puts(name_hd)
      @collection.find(eval(query), eval(opts_for_top)) do |cursor|
        cursor.each do |doc|
          name = doc['n']
          version_code = doc['verc'].nil? ? '' : doc['verc']
          dct = doc['dct']
          # Limit the results to a number of rows.
          if !@price.nil? and count >= @limit
            break
          end
          # Return unique package names
          if not top_package_names_list.include? name
            top_package_names_list << name
            line = name + "," + version_code + "," + dct.to_s
            @@log.info(line)
            file.puts(line)
            if !@price.nil?
              count += 1
            end
          end
        end
      end
    end
    #2) Write the results of bottom apps.
    count = 0
    bottom_package_names_list = []
    bottom_out_file = File.join(@out_dir, bottom_file_name)
    File.open(bottom_out_file, 'w') do |file|
      file.puts(name_hd)
      @collection.find(eval(query), eval(opt_for_bottom)) do |cursor|
        cursor.each do |doc|
          name = doc['n']
          version_code = doc['verc'].nil? ? '' : doc['verc']
          dct = doc['dct']
          # Limit the results to a number of rows.
          if !@price.nil? and count >= @limit
            break
          end
          # Return unique package names
          if not bottom_package_names_list.include? name
            bottom_package_names_list << name
            line = name + "," + version_code + "," + dct.to_s
            @@log.info(line)
            file.puts(line)
            if !@price.nil?
              count += 1
            end
          end
        end
      end
    end
    @@log.info("The top apps list has been written to: #{top_out_file}")
    @@log.info("The bottom apps list has been written to: #{bottom_out_file}")          
    
  end
  
  # Find top/bottom apps that use neither of the given permissions.
  def find_top_bottom_apps_not_in_any_permission
    collection_name = nil
    file_name = nil
    query = nil
    
    # Prepare the query to the collection.
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
        query = "{ 'pri' => 'Free', 'per' => { '$nin' => #@per_list }, 'verc' => {'$ne' => nil} }"
        file_name = "free" + "#{file_name_per_part}" + "apps.csv"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'per' => { $nin: '#@per_list' } }"
        file_name = "paid" + "#{file_name_per_part}" + "apps.csv"
      else
        query = "{'per' => { $nin: '#@per_list' } }"
        file_name = "#{file_name_per_part}" + "apps.csv"
      end
    else
      @@log.error("Permission list is empty.")
      return
    end
    
    # Result files
    top_file_name = 'top_neither_' + file_name
    bottom_file_name = 'bottom_neither_' + file_name
    # Set the sort order for top/bottom results
    opts_for_top = "{ :sort => [['dct', Mongo::DESCENDING]], :timeout => false}"
    opt_for_bottom ="{ :sort => [['dct', Mongo::ASCENDING]], :timeout => false}"
    
    # write the results into two files
    #1) Write the results of top apps.
    count = 0
    top_package_names_list = []
    name_hd = "apk_name,version_code,download_count"
    top_out_file = File.join(@out_dir, top_file_name)
    File.open(top_out_file, 'w') do |file|
      file.puts(name_hd)
      @collection.find(eval(query), eval(opts_for_top)) do |cursor|
        cursor.each do |doc|
          name = doc['n']
          version_code = doc['verc'].nil? ? '' : doc['verc']
          dct = doc['dct']
          # Limit the results to a number of rows.
          if !@price.nil? and count >= @limit
            break
          end
          # Return unique package names
          if not top_package_names_list.include? name
            top_package_names_list << name
            line = name + "," + version_code + "," + dct.to_s
            @@log.info(line)
            file.puts(line)
            if !@price.nil?
              count += 1
            end
          end
        end
      end
    end
    #2) Write the results of bottom apps.
    count = 0
    bottom_package_names_list = []
    bottom_out_file = File.join(@out_dir, bottom_file_name)
    File.open(bottom_out_file, 'w') do |file|
      file.puts(name_hd)
      @collection.find(eval(query), eval(opt_for_bottom)) do |cursor|
        cursor.each do |doc|
          name = doc['n']
          version_code = doc['verc'].nil? ? '' : doc['verc']
          download_count = doc['dct']
          # Limit the results to a number of rows.
          if !@price.nil? and count >= @limit
            break
          end
          # Return unique package names
          if not bottom_package_names_list.include? name
            bottom_package_names_list << name
            line = name + "," + version_code + "," + download_count.to_s
            @@log.info(line)
            file.puts(line)
            if !@price.nil?
              count += 1
            end
          end
        end
      end
    end
    @@log.info("The top apps list has been written to: #{top_out_file}")
    @@log.info("The bottom apps list has been written to: #{bottom_out_file}")    
  end
  
  # Find top apps that have version code numbers.
  def find_top_apps
    query = "{}"
    opts = "{ :fields => ['n', 'dct'], :sort => [['dct', Mongo::DESCENDING]], :limit => #@limit, :timeout => false}"
    file_name = "top_apps.csv"
    if(!@price.nil?)
       if(@price.casecmp("free") == 0)
         query = "{ 'pri' => 'Free', 'verc' => {'$ne' => nil} }"
         file_name = "top_free_apps.csv"
       elsif(@price.casecmp("paid") == 0)
         query = "{ 'pri' => {'$ne' => 'Free'}, 'verc' => {'$ne' => nil} }"
         file_name = "top_paid_apps.csv"
       end
    end
    if(!@per_name.nil?)
      if(!@price.nil? and @price.casecmp("free") == 0)
        query = "{ 'pri' => 'Free', 'verc' => {'$ne' => nil}, 'per' => '#@per_name' }"
        file_name_per_part = @per_name.split('.')[-1]
        file_name = "top_free_" + "#{file_name_per_part}" + "_apps.csv"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'verc' => {'$ne' => nil}, 'per' => '#@per_name' }"
        file_name = "top_paid_" + "#@per_name.split('.')[-1]" + "_apps.csv"
      else
        query = "{'per' => '#@per_name', 'verc' => {'$ne' => nil} }"
        file_name = "top_" + "#@per_name.split('.')[-1]" + "_apps.csv"
      end
    end
    # set the result collection name
    map = {' ' => '', '-' => '_', ':' => '_'}
    regex = Regexp.new(map.keys.map { |x| Regexp.escape(x) }.join('|'))
    collection_name = "top_apps_" + Time.now.to_s.gsub(regex, map)
    
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
    opts_for_top = nil
    if(!@limit.nil?)
      opts_for_top = "{ :sort => [['_id.download', Mongo::DESCENDING]], :limit => #@limit}"
    else
      opts_for_top = "{ :sort => [['_id.download', Mongo::DESCENDING]]}"
    end
    # write the results into two files.
    name_hd = "apk_name,download_count"
    top_out_file = File.join(@out_dir, file_name)
    File.open(top_out_file, 'w') do |file|
      file.puts(name_hd)
      custom_collection.find(Hash.new(0), eval(opts_for_top)).each do |doc|
        name = doc['_id']['apk_name']
        dct = doc['_id']['download']
        line = name + "," + dct.to_s
        @@log.info(line)
        file.puts(line)
      end
    end
    # Drop the temporarily collection
    custom_collection.drop()
    @@log.info("The top apps list has been written to: #{top_out_file}")
  end
  
  # Find bottom apps that have version code numbers.
  def find_bottom_apps
    query = "{}"
    opts = "{ :fields => ['n', 'dct'], :sort => [['dct', Mongo::ASCENDING]], :limit => #@limit, :timeout => false}"
    file_name = "bottom_apps.csv"
    if(!@price.nil?)
       if(@price.casecmp("free") == 0)
         query = "{ 'pri' => 'Free', 'verc' => {'$ne' => nil} }"
         file_name = "bottom_free_apps.csv"
       elsif(@price.casecmp("paid") == 0)
         query = "{ 'pri' => {'$ne' => 'Free'}, 'verc' => {'$ne' => nil} }"
         file_name = "bottom_paid_apps.csv"
       end
    end
    if(!@per_name.nil?)
      if(!@price.nil? and @price.casecmp("free") == 0)
        query = "{ 'pri' => 'Free', 'verc' => {'$ne' => nil}, 'per' => '#@per_name' }"
        file_name_per_part = @per_name.split('.')[-1]
        file_name = "bottom_free_" + "#{file_name_per_part}" + "_apps.csv"
      elsif(!@price.nil? and @price.casecmp("paid") == 0)
        query = "{ 'pri' => {'$ne' => 'Free'}, 'verc' => {'$ne' => nil}, 'per' => '#@per_name' }"
        file_name = "bottom_paid_" + "#@per_name.split('.')[-1]" + "_apps.csv"
      else
        query = "{'per' => '#@per_name', 'verc' => {'$ne' => nil} }"
        file_name = "bottom_" + "#@per_name.split('.')[-1]" + "_apps.csv"
      end
    end
    # set the result collection name
    map = {' ' => '', '-' => '_', ':' => '_'}
    regex = Regexp.new(map.keys.map { |x| Regexp.escape(x) }.join('|'))
    collection_name = "bottom_apps_" + Time.now.to_s.gsub(regex, map)
    
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
    opts_for_bottom = nil
    if(!@limit.nil?)
      opts_for_bottom = "{ :sort => [['_id.download', Mongo::ASCENDING]], :limit => #@limit}"
    else
      opts_for_bottom = "{ :sort => [['_id.download', Mongo::ASCENDING]]}"
    end
    # write the results into two files.
    name_hd = "apk_name,download_count"
    bottom_out_file = File.join(@out_dir, file_name)
    File.open(bottom_out_file, 'w') do |file|
      file.puts(name_hd)
      custom_collection.find(Hash.new(0), eval(opts_for_bottom)).each do |doc|
        name = doc['_id']['apk_name']
        dct = doc['_id']['download']
        line = name + "," + dct.to_s
        @@log.info(line)
        file.puts(line)
      end
    end
    # Drop the temporarily collection
    custom_collection.drop()
    @@log.info("The bottom apps list has been written to: #{out_file}")
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
        if(@per_name.nil?)
          puts "Please use the -P option to specify a permission or a set of permissions in a comma-separated values format."
          abort(@@usage)
        else
          @per_list = [@per_name]
        end
      end
      find_top_bottom_apps_in_any_permission
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
        puts "Error: Please use the -k option to specify the file that contains package names."
        abort(@@usage)
      elsif File.file?(@package_names_file)
        write_apps_description_by_package_name
      else
        puts "Error: package names file #{@package_names_file} does not exist."
        exit
      end
    elsif(cmd.eql? "write_apps_description")
      write_apps_description
    elsif(cmd.eql? "find_version_code")
      if(@package_names_file.nil?)
        puts "Error: Please use the -k option to specify the file that contains package names."
        abort(@@usage)
      elsif File.file?(@package_names_file)
        find_version_code
      else
        puts "Error: package names file #{@package_names_file} does not exist."
        exit
      end
    elsif(cmd.eql? "find_app_info")
      if(@package_names_file.nil?)
        puts "Error: Please use the -k option to specify the file that contains package names and version code values."
        abort(@@usage)
      elsif File.file?(@package_names_file)
        find_app_info
      else
        puts "Error: package names file #{@package_names_file} does not exist."
        exit
      end
    end
    
    close_mongodb_connection
    end_time = Time.now
    elapsed_time = end_time - beginning_time
    @@log.info("Finished after #{Time.at(elapsed_time).utc.strftime("%H:%M:%S")}")
  end

  public
  def command_line(args)
    log_file_name = nil
    begin
      opt_parser = OptionParser.new do |opts|
        opts.banner = @@usage + @@cmd_desc
        opts.on('-h','--help', 'Show this help message and exit') do
          puts opts
          exit
        end
        opts.on('-l','--log <log_file>', 'Write error level logs to the specified file.') do |log_file|
          log_file_name = log_file
        end
        opts.on('-H','--host <host_name>', 'The host name that the mongod is connected to.', 'Default value is localhost.') do |host_name|
          @host = host_name
        end
        opts.on('-p','--port <port>', Integer, 'The port number that the mongod instance is listening.', 'Default port number is 27017.') do |port_num|
          @port = port_num
        end
        opts.on('-u','--user <user_name>', 'A username with which to authenticate to a MongoDB database', 'that uses authentication. Use it in conjunction with the --password.') do |user_name|
          @db_user = user_name
        end
        opts.on('-s','--password <password>', 'A password with which to authenticate to a MongoDB database', 'that uses authentication. Use it in conjunction with the --user.') do |password|
          @db_pw = password
        end
        opts.on('-d','--database <database>', 'The name of the database that holds the public collection in MongoDB.', 'Default value is apps') do |dbname|
          @db_name = dbname
        end
        opts.on('-c','--database <database>', 'The name of the public collection in MongoDB.', 'Default value is public') do |dbcollection|
          @db_collection_name = dbcollection
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
        opts.on('-m','--max <value>', Integer, 'The maximum number of documents to return.') do |max_value|
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
    elsif(args[0].eql? "write_apps_description")
      cmd = "write_apps_description"
    elsif(args[0].eql? "find_version_code")
      cmd = "find_version_code"
    elsif(args[0].eql? "find_app_info")
      cmd = "find_app_info"
    else
      puts "Error: Unknown command."
      abort(@@usage)
    end
    
    if(args[1].nil?)
      puts("Results output direcotry is missing.")
      abort(@@usage)
    else
      Log.log_file_name = log_file_name
      @@log = Log.instance
      out_dir = File.absolute_path(args[1])
      start_main(out_dir, cmd)
    end
  end
end


if __FILE__ == $PROGRAM_NAME
  driver_obj = MongodbDriver.new
  driver_obj.command_line(ARGV)
end

