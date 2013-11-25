class FilesFinder
  attr_accessor :absolute_path_name, :extension_name
  def initialize(absolute_path_name, extension_name)
    @absolute_path_name = absolute_path_name
    @extension_name = extension_name
    @files = Array.new
  end

  public
  def find_files(verbose = false)
    if(!File.exist? @absolute_path_name)
      puts 'Error: No such file or directory'
      return nil
    end
    @verbose = verbose
    files_listing(@absolute_path_name, @extension_name)
    return @files
  end

  private
  def files_listing(source, ext_name)
    Dir.entries(source).select do |item|
      next if item == '.' or item == '..'
      file = File.join(source, item)
      if(File.directory?(file))
        files_listing(file, ext_name)
      elsif(File.extname(file).downcase.eql? ext_name)
	@files << file
	if @verbose
	  puts file
	end
      end
    end
  end
end
