require 'json'

class App
  attr_reader :name
  attr_accessor :title, :playStoreURL, :category, :price, :datePublished, :version, :operatingSystems, 
  :ratingsCount, :rating, :contentRating, :creator, :creatorURL, :installSize, :installSizeText, 
  :downloadsCount, :downloadsCountText, :description, :reviews, :permissions
  
  def initialize(name)
    @name = name
  end
  
  def to_json
    {'name' => @name, 'title' => @title, 'description' => @description, 'playStoreURL' => @playStoreURL, 
    'category' => @category, 'price' => @price, 'datePublished' => @datePublished, 'version' => @version, 
    'operatingSystems' => @operatingSystems, 'ratingsCount' => @ratingsCount, 'rating' => @rating, 
    'contentRating' => @contentRating, 'creator' => @creator, 'creatorURL' => @creatorURL, 
    'installSize' => @installSize, 'installSizeText' => @installSizeText, 'downloadsCount' => @downloadsCount, 
    'downloadsCountText' => @downloadsCountText, 'permissions' => @permissions, 'reviews' => @reviews
    }.to_json
  end

end
