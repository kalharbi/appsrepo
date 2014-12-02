require 'open3'
require_relative '../utils/settings'
require_relative '../utils/log'

class AaptExecutor
  
  @@log = Log.instance
  attr_reader :aapt_path, :apk_path
  
  def initialize(apk_path)
    @apk_path = apk_path
  end
  
  private
  def execute_aapt(what)
    out = nil
    Open3.popen3(Settings.aapt, 'dump', what, @apk_path) {|stdin, stdout, stderr, wait_thr|
      # Waits the termination of the process
      exit_status = wait_thr.value 
      out = stdout.gets(nil)
      err = stderr.gets(nil)
      if err
        @@log.error(err.to_s)
      end
    }
    out
  end
  
  public
  def get_version_info
    version_info = Hash.new
    aapt_out = execute_aapt("badging")
    if aapt_out.nil?
      return version_info
    end
    line = aapt_out.lines.first
    segment = line.strip.split(":")
    if(!segment.nil? and segment.length >1)
      if(segment[0].eql? "package")
        package_info = segment[1].strip.split(' ')
        package_info.each do |info_line|
          info = info_line.strip.split('=')
          if(info[0].eql? "versionCode")
            version_info[:version_code] = info[1].tr("'", "") 
            # Remove the ' character from the string value
          elsif(info[0].eql? "versionName")
            version_info[:version_name] = info [1].tr("'", "")
          end
        end
      end
    end
    # Return a hash of version code and version name
    return version_info
  end
end
