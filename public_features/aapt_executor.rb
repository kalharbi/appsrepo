require_relative '../utils/logging'
require_relative '../utils/settings'

class AaptExecutor
   attr_reader :aapt_path, :apk_path
   
   def initialize(apk_path)
     @apk_path = apk_path
   end
   
   private
   def execute_aapt(what)
     args = "dump #{what} " + @apk_path
     result = `#{Settings.aapt} #{args}`.split(/\r?\n/)
   end
   
   public
   def get_version_info
     version_info = Hash.new
     aapt_out = execute_aapt("badging")
     aapt_out.each do |line|
       segment = line.strip.split(":")
       if(!segment.nil? and segment.length >1)
         if(segment[0].eql? "package")
           package_info = segment[1].strip.split(' ')
           package_info.each do |info_line|
             info = info_line.strip.split('=')
             if(info[0].eql? "versionCode")
               version_info[:version_code] = info[1].tr("'", "") # Remove the ' character from the string value
             elsif(info[0].eql? "versionName")
               version_info[:version_name] = info [1].tr("'", "")
             end
           end
           break # Break from the loop after getting the required verions info
         end
       end
     end
     # Return a hash of version code and version name
     return version_info
   end
 end