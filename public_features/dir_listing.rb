def directory_listing(source)
  if(!File.exist? source)
    aborts("Error: No such file or directory")
  end
  path = source
  json_files = Array.new
  Dir.entries(source).select do |item|
    next if item == '.' or item == '..'
    file = File.absolute_path(path)
    if(File.directory?(file))
      path = File.join(path, item)
      puts "got directory #{file}"
      directory_listing(file)
    elsif(File.extname(file).downcase.eql? ".json")
      json_files << file
    end
  end
  json_files
end