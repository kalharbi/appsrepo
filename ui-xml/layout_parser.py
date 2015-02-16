import os.path
import re
from lxml import etree
from xml.etree import ElementTree
from lxml.etree import ParserError
from lxml.etree import XMLSyntaxError

class LayoutParser(object):
        
    def start_parser(self, layout_file, apk_dir):
        root = etree.parse(layout_file)
        for child in root.iter():
            if child.tag == 'merge':
                return
            elif child.tag == 'include':
                embeded_layout = child.get('layout')
                embeded_dir, embeded_file = embeded_layout[1:].split('/')
                embeded_file_full_path = os.path.join(apk_dir, 'res', embeded_dir, 
                                                      embeded_file + '.xml')
                # Get the tree of the included layout
                emebeded_tree = LayoutParser().parse(embeded_file_full_path,
                                                                apk_dir)
                child.getparent().append(emebeded_tree.getroot())
                # Remove the include tag
                child.getparent().remove(child)
            else:
                attributes = dict(child.attrib)
                for attr_name, attr_value in attributes.iteritems(): 
                    if '@' in attr_value:
                        res_element = re.match(r'@(.*?)/',attr_value).group(1)
                        res_file_base_name = os.path.join(res_element + 's.xml')
                        res_file = os.path.join(apk_dir, 'res', 'values',
                                                res_file_base_name)
                        res_attr = attr_value.split('/')[1]
                        if res_element != 'id' and res_element != '+id':
                            ref_value = self.find_attr_value(res_file, res_element,
                                                             res_attr)
                            if ref_value is not None and len(ref_value) > 0:
                                child.set(attr_name, ' '.join(ref_value))
        return root
                
        
    # Search for a string resource value in an xml file such as strings.xml
    @staticmethod
    def find_attr_value(xml_file, element_name, attribute_name):
        try:
            if not os.path.exists(xml_file):
                print('Error: Resource file does not exist, ' + xml_file)
                return []
            tree = etree.parse(xml_file)
            if attribute_name is not None:
                xpath_query = "//" + element_name + '[@name="' + attribute_name + '"]/text()'
                return tree.xpath(xpath_query,
                  namespaces={'android': "http://schemas.android.com/apk/res/android"})
        except (ParserError, XMLSyntaxError) as e:
            print("Error in file: %s", xml_file)
        return []
    
    def parse(self, layout_file, apk_dir):
        return self.start_parser(layout_file, apk_dir)
        
    