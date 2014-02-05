#!/usr/bin/env ruby
require 'optparse'

class WordsChecker
  @@usage = "Usage: #{$PROGRAM_NAME} file1 file2 [-h | -m word | sentence ]"
  attr_accessor :mode
  def initialize
    @mode ='word'  
  end
  
  def start_main(file1, file2)
    if(@mode.eql?"sentence")
      compare_sentences(file1, file2)
    elsif(@mode.eql?"word")
      compare_words(file1,file2)
    end
  end

  def compare_sentences(file1_path, file2_path)
    file2 = File.open(file2_path)
    content = file2.read
    total = found = notfound = 0
    File.readlines(file1_path).each  do |line|  
      next unless line.split.size > 1
      total += 1
      if(content.include?(line.strip))
        found += 1
      else
        puts "Not found: #{line}"
        notfound += 1
      end
    end
    print_results("sentences",total, found, notfound)
  end
  
  def compare_words(file1_path, file2_path)
    file2 = File.open(file2_path)
    content = file2.read
    total = found = notfound = 0
    File.readlines(file1_path).each  do |line|  
      line.split.each do |word|
        total += 1
        # remove special characters
        word = word.gsub(/[^a-zA-Z0-9\-]/,"")
        if(content.include?(word))
          found += 1
        else
          puts "Not found: #{word}"
          notfound += 1
        end
      end
    end
    print_results("words",total, found, notfound)
  end
  
  def print_results(mode, total, found, notfound)
    puts "#############################################################"
    puts "Total #{mode} #{total}. Found: #{found}. Not found: #{notfound}."
    success_rate = ((found.to_f / total.to_f ) * 100.0).round(2)
    puts "Success rate: #{success_rate} %"
    puts "#############################################################"
  end

  def command_line(argv)
    begin
      opt_parser = OptionParser.new do |opts|
        opts.banner = @@usage
        opts.on('-h','--help', 'Show this help message and exit.') do
          puts opts
          exit
        end
        opts.on('-m','--mode <mode>', 'The comparison mode. Valid values are: word or sentence.') do |mode_val|
          if(mode_val.downcase.eql?"sentence") 
            @mode = "sentence"
          elsif(mode_val.downcase.eql?"word")
            @mode = "word"
          else
            abort("Invalid mode: #{mode_val} valid values are sentence or word")
          end    
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
    
    if(argv[0].nil? || argv[1].nil?)
      abort(@@usage)
    else
      file1 = File.absolute_path(argv[0])
      file2 = File.absolute_path(argv[1])
      if(!File.exist? file1)
        puts "Error: No such file: #{file1}"
        abort(@@usage)
      elsif(!File.exist? file2)
         puts "Error: No such file: #{file2}"
         abort(@@usage)
      end
      start_main(file1, file2)
    end
  end
end


if __FILE__ == $PROGRAM_NAME
  main_obj = WordsChecker.new
  main_obj.command_line(ARGV)
end
