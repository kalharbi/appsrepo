require 'json'
require_relative 'app'

class JsonReader
  attr_reader :json_file
  
  public 
  def parse_json_data(json_file)
    serialized = File.read(json_file)
    data = JSON.parse(serialized)
    name = File.basename(json_file,".json")
    app = convert_to_object(name, data)
    app.to_json
  end
  
  private
  def convert_to_object(name, data)
    app = App.new(name)
    app.title = data["title"]
    app.playStoreURL = data["playStoreURL"]
    app.category = data["category"]
    app.price = data["price"]
    app.datePublished = data["datePublished"]
    app.version = data["version"]
    app.operatingSystems = data["operatingSystems"]
    app.ratingsCount = data["ratingsCount"]
    app.rating = data["rating"]
    app.contentRating = data["contentRating"]
    app.creator = data["creator"]
    app.creatorURL = data["creatorURL"]
    app.installSize = convert_install_size_text_to_KBytes(data["extendedInfo"]["installSize"])
    app.installSizeText = data["extendedInfo"]["installSize"]
    app.downloadsCount = data["extendedInfo"]["downloadsCount"]
    app.downloadsCountText = data["extendedInfo"]["downloadsCountText"]
    app.description = data["extendedInfo"]["description"]
    app.reviews = data["extendedInfo"]["reviews"]
    app.permissions = data["extendedInfo"]["permissions"]
    app
  end
  
  private
  def convert_install_size_text_to_KBytes(sizeText)
    unit = sizeText[-1].downcase
    size = sizeText.to_f
    case unit
    when "k"
      size
    when "m"
      size *= 1024
    when "g"
      size *= 1024*1024
    else
      unless(is_number?(size))
        abort("Unknown file size #{sizeText}")
      end
    end
  end
  
  private
  def is_number?(number)
    true if Float(number) rescue false
  end

end
