require 'json'
require 'date'
require_relative 'app'
require_relative 'app_review'
require_relative '../utils/log'

class JsonReader
  
  @@log = Log.instance
  attr_reader :json_file
  
  public
  def parse_json_data(json_file)
    begin
      serialized = File.read(json_file)
      data = JSON.parse(serialized)
      name = File.basename(json_file,".json")
      app = convert_to_object(name, data)
    rescue Exception => e 
      @@log.error("Error in JSON file: #{json_file} - #{e.message}")
      return nil
    end
  end
  
  private
  def convert_to_object(name, data)
    name = remove_download_date_from_apk_name(name)
    app = App.new(name)
    app.title = data["title"]
    app.playStoreURL = data["playStoreURL"]
    app.category = data["category"]
    app.price = get_price_value(data["price"])
    app.datePublished = convert_string_to_date(data["datePublished"])
    app.operatingSystems = data["operatingSystems"]
    app.ratingsCount = data["ratingsCount"]
    app.rating = data["rating"]
    app.contentRating = data["contentRating"]
    app.creator = data["creator"]
    app.creatorURL = data["creatorURL"]
    app.installSize = convert_install_size_text_to_KBytes(data["extendedInfo"]["installSize"])
    app.installSizeText = data["extendedInfo"]["installSize"]
    app.downloadsCount = convert_download_text_to_number(data["extendedInfo"]["downloadsCountText"])
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
  
  def get_price_value(price)
    if !price.nil? and price.eql? '0'
      price = 'Free'
    end
    price
  end

  # Remove the download date from the apk name.
  # This is done because the crwaler appends the download date into the file name
  # Example: com.google.android.apps.googlevoice.20130926 ->com.google.android.apps.googlevoice
  def remove_download_date_from_apk_name(apk_name)
    date_index = apk_name.rindex('.201')
    if !date_index.nil?
      if is_number?(apk_name[-8..-1])
        apk_name = apk_name[0..-10]
      end
    end
    apk_name
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
  
  def convert_download_text_to_number(download_range)
    index = download_range.index('-')
    download_count = 0
    if !index.nil?
      download_text_value = download_range[0..index]
      download_count = download_text_value.gsub(/[^\d]/, '').to_i
    end
    download_count
  end

  def convert_string_to_date(string_date)
   begin
     return Date.parse string_date
   rescue ArgumentError => e
     @@log.error("Date conversion error in file: #{@json_file} - #{e.message}")
     return string_date
   end
  end

  def is_number?(number)
    true if Float(number) rescue false
  end

end
