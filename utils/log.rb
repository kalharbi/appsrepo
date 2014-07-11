require 'logging'

module Log
  
  @log_file_name = nil
    
  def Log.config_log(log_file_name = nil)
    @log_file_name = log_file_name
  end
  
  def Log.logger
    @logger
  end
  
  def Log.file_logger
    @file_logger
  end
  
  def self.logger
    @logger = Logging.logger(STDOUT)
    @logger.level = :info
    @logger
  end
  
  def self.file_logger
    @file_logger = Logging.logger[self]
    @file_logger.level = :error
    if @log_file_name.nil?
      file_name = $PROGRAM_NAME + '-'  + Time.new.strftime("%Y-%m-%d") + ".log"
      @log_file_name = File.open(file_name, 'a+')
    end
    
    Logging.appenders.rolling_file(
        @log_file_name,
        :layout => Logging.layouts.pattern(
            :pattern => '%.1l, [%d] %5l -- %c: %m\n',
            :date_pattern => "%Y-%m-%dT%H:%M:%S.%s"
        )
      )
    @file_logger.add_appenders @log_file_name
    
  end
  
end
