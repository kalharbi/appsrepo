require 'logger'

module Logging
  @log_dev = STDOUT
  @level = Logger::INFO

  def self.config_log(config)
    if(!config['dev'].nil?)
      log_dev = config['dev']
      if (log_dev != 'STDOUT')
        @log_dev = File.open(log_dev, File::WRONLY | File::APPEND | File::CREAT)
      end
    end
    
    if (!config['level'].nil?)
      level = config['level'].downcase
      if(level == 'error')
        @level = Logger::ERROR
      elsif(level == 'warning')
        @level = Logger::WARN
      elsif(level == 'info')
        @level = Logger::INFO
      end
    end

  end

  def logger
    Logging.logger
  end
  
  def self.logger
    @logger ||= Logger.new(@log_dev)
    @logger.level = @level
    @logger
  end

end
