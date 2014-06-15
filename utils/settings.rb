module Settings
  
  # It's a singleton, so instantation is not allowed.
  extend self

  attr_reader :settings
  
  public
  def load(conf_file)
    raise "The configuration file #{conf_file} does not exist!" unless File.exists?(conf_file)
    @settings = Hash.new
    store_conf(conf_file)
  end
  
  private
  def store_conf(conf_file)
    File.readlines(conf_file).each do |line|
      # Skip comments and empty lines
      next if line.match(/^#/)
      next if line.match(/^$/)
      var = line.strip.split('=')
      # Use symbols as hash keys
      key = var[0].to_s.strip
      value = var[1].strip
      @settings[key.to_sym] = value
      # create method for each key name
      define_method(var[0].strip.to_s) { @settings[key.to_sym] }
    end
  end
  
  def method_missing(name, *args, &block)
      @settings[name.to_sym] ||
      fail(NoMethodError, "unknown configuration name #{name}", caller)
  end
  
end
