require 'json'

class AppReview
  attr_accessor :timestampMsec, :starRating, :title, :comment, :commentId,
  :author, :authorURL, :authorSecureURL
  
  def get_review
    review = {'ts' => @timestampMsec, 'st' => @starRating, 't' => @title, 
              'cmt' => @comment, 'id' => @commentId, 'a' => @author,
              'url' => @authorURL, 'surl' => @authorSecureURL
            }
  end

end
