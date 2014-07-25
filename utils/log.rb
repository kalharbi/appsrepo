require 'logging'
require 'singleton'

class Log
  include Singleton
  
  @@file_name = nil
  attr_accessor :log_file_name
  
  def initialize
    # set file log name
    if @@file_name.nil?
      @log_file_name = $PROGRAM_NAME + '-'  + Time.new.strftime("%Y-%m-%d") + ".log"
    else
      @log_file_name = @@file_name
    end
    
    # only show "info" or higher messages on STDOUT using the Basic layout
    Logging.appenders.stdout(:level => :info)
    
    begin
      # send all error log events to the file log as JSON
      Logging.appenders.rolling_file(
        @log_file_name,
        :level  => :error,
        :age    => 'daily',
        :layout => Logging.layouts.json
        )
    rescue ArgumentError => e
      abort(e.message)
    end
    @logger ||= Logging.logger['appsrepo']
    @logger.level = :info
    @logger.add_appenders @log_file_name, 'stdout'
  end
  
  def self.log_file_name=log_file_name
    @@file_name = log_file_name
  end
   
  def error(msg)
     @logger.error(msg)
  end
  
  def warning(msg)
    @logger.warn(msg)
  end
  
  def info(msg)
    @logger.info(msg)
  end
  
  def debug(msg)
    @logger.debug(msg)
  end
  
end
