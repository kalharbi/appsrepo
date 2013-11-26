require 'logger'

module Logging
  @log_dev = STDOUT
  
  def self.config_log(config)
    log_dev = config['logdev']
    if (log_dev != 'STDOUT')
      log_file = File.open(log_dev, File::WRONLY | File::APPEND | File::CREAT)
      @log_dev = log_file
    end
  end

  def logger
    Logging.logger
  end
  
  def self.logger
    @logger ||= Logger.new(@log_dev)
    @logger.level = Logger::INFO
    @logger
  end

end
