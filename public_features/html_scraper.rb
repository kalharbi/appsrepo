require 'nokogiri'
require_relative '../utils/log'

class HtmlScraper
  @@log = Log.instance
  attr_reader :html_file
  
  def initialize(html_file)
    @html_file = html_file
  end
  
  private
  def parse_html_file
    begin
      page = Nokogiri::HTML(open(@html_file))
    rescue Errno::ENOENT
      @@log.error("HTML file does not exist: #@html_file")
    end
  end
  
  public
  def get_what_is_new
    page = parse_html_file
    if(page.nil?)
      @@log.error("Could not read HTML file: #@html_file")
      return []
    end
    new_changes_list = page.css('div.details-section-contents div.recent-change')
    changes = []
    new_changes_list.each do |change|
      changes << change.text.strip
    end
    changes
  end
end
  
