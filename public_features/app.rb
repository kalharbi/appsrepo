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
    app_info = {'n' => @name, 't' => @title, 'desc' => @description, 
        'url' => @playStoreURL, 'cat' => @category, 'pri' => @price, 
        'dtp' => @datePublished, 'ver' => @version, 
        'os' => @operatingSystems, 'rct' => @ratingsCount, 'rate' => @rating, 
        'crat' => @contentRating, 'crt' => @creator, 'curl' => @creatorURL, 
        'sz' => @installSize, 'sztxt' => @installSizeText, 
        'dct' => @downloadsCount, 'dtxt' => @downloadsCountText, 
        'per' => @permissions, 'rev' => @reviews}
    JSON.parse(app_info.to_json)
  end
end
