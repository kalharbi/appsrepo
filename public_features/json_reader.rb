require 'json'
require_relative 'app'
require_relative 'app_review'
require_relative '../utils/logging'

class JsonReader
  attr_reader :json_file
  
  public 
  def parse_json_data(json_file)
    begin
      serialized = File.read(json_file)
      data = JSON.parse(serialized)
      name = File.basename(json_file,".json")
      app = convert_to_object(name, data)
      app.to_json
    rescue JSON::ParserError
      Logging.logger.error("Error in file: #{json_file}")
      return nil
    end
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
    app.reviews = get_app_review(data["extendedInfo"]["reviews"])
    app.permissions = data["extendedInfo"]["permissions"]
    app
  end
  
  private
  def get_app_review(reviews)
    new_review = []
    if reviews.nil? || reviews.empty?
      return new_review
    end
    reviews.each do |review|
      app_review = AppReview.new
      app_review.timestampMsec = review["timestampMsec"]
      app_review.starRating = review["starRating"]
      app_review.title = review["title"]
      app_review.comment = review["comment"]
      app_review.commentId = review["commentId"]
      app_review.author = review["author"]
      app_review.authorURL = review["authorURL"]
      app_review.authorSecureURL = review["authorSecureURL"]
      new_review << app_review.get_review
    end
    new_review
  end

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
