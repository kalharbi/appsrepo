require 'nokogiri'
require_relative '../utils/logging'

class HtmlScraper
  attr_reader :html_file
  
  def initialize(html_file)
    @html_file = html_file
  end
  
  private
  def parse_html_file
    begin
      page = Nokogiri::HTML(open(@html_file))
    rescue Errno::ENOENT
      Logging.logger.error("Error: No such file or directory: #@html_file.")
    end
  end
  
  public
  def get_what_is_new
    page = parse_html_file
    if(page.nil?)
      return nil
    end
    new_changes_list = page.css('div.details-section-contents div.recent-change')
    changes = []
    new_changes_list.each do |change|
      changes << change.text.strip
    end
    changes
  end
end
  