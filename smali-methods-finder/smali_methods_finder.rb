#!/usr/bin/env ruby
require 'optparse'
require '../utils/logging'

class SmaliMethodsFinder
  
  @@usage = "Usage: #{$PROGRAM_NAME} dir_to_unpacked_apks [OPTIONS]"
  attr_reader :mode
  
  def initialize
    @mode = "all"
  end
  
  private
  def find_app_methods(file_name, dir_name)
    dest_file_name = File.basename(file_name, File.extname(file_name)) + ".methods.txt"
    dest_file_path = File.join(dir_name, dest_file_name)
    if(File.exists? dest_file_path)
      File.delete(dest_file_path)
    end
    File.open(dest_file_path, 'w') do |out_file|
      File.open(file_name, 'r').each_line do |s|
        if s.start_with?(".method")
          last_index = s.index('(')
          sub_word = s[0, last_index]
          first_index = sub_word.rindex(' ') + 1
          method_name = sub_word[first_index,last_index]
          if method_name.lstrip.length > 1
            out_file.write(method_name + "\n")
          end
        end
      end
    end
  end
  
  private
  def find_invoked_api_methods(file_name, dir_name)
    dest_file_name = File.basename(file_name, File.extname(file_name)) + ".invoke.txt"
    dest_file_path = File.join(dir_name, dest_file_name)
    if File.exists?(dest_file_path)
       File.delete(dest_file_path)
    end
    File.open(dest_file_path, 'w') do |out_file|
      File.open(file_name, "r").each_line do |s|
        if s.lstrip.start_with?("invoke-")
          last_index = s.index('(')
          sub_word = s[0, last_index]
          first_index = sub_word.rindex('>') + 1
          method_name = sub_word[first_index,last_index]
          if method_name.lstrip.length > 1
            out_file.write(method_name + "\n")
          end
        end
      end
    end
  end
  
  private
  def start_main(source)
    beginning_time = Time.now
    if(!File.exist? source || !File.directory?(source)) 
      puts "Error: No such directory"
      abort(@@usage)
    end 
    dest_dir = File.absolute_path(source)
    # Run smali parser to parse and extract method names
    cmd = "java -jar ./bin/smali-words-extractor-1.3.jar -input #{dest_dir} -pool 2"
    `#{cmd}`
    
    apk_dirs = Dir.glob(dest_dir + '/*/').each do |apk_dir_path|
      puts apk_dir_path
      apk_name = File.basename apk_dir_path
      methods_dir = File.join(apk_dir_path, "methods")
      methods_file_name = apk_name + ".txt"
      methods_file_path = File.join(File.absolute_path(methods_dir), methods_file_name)
      Logging.logger.info(methods_file_path)
      if(@mode.eql?"find_app_methods")
        find_app_methods(methods_file_path, methods_dir)
      elsif(@mode.eql? "find_invoked_api_methods")
        find_invoked_api_methods(methods_file_path, methods_dir)
      elsif(@mode.eql? "all")
        find_app_methods(methods_file_path, methods_dir)
        find_invoked_api_methods(methods_file_path, methods_dir)
      else
        abort("Unknown mode: Please use find_app_methods OR find_invoked_api_methods")
      end
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
        opts.on('-l','--log <log_file,[level]>', Array, 'Write logs to the specified file with the given logging level such as error or info. The default logging level is info.') do |log_options|
	  log_level = 'info'
	  if(!log_options[1].nil?)
	    log_level = log_options[1]
	  end
	  config = {"dev" => log_options[0], "level" => log_level}
	  Logging.config_log(config)
        end
        opts.on('-f','--find <find_app_methods | find_invoked_api_methods>', 
        "The running mode. It must be one of the following: find_app_methods or find_invoked_api_methods.
        The default mode is to find both user's declared methods and Android API methods.") do |mode|
          @mode = mode
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
  main_obj = SmaliMethodsFinder.new
  main_obj.command_line(ARGV)
end