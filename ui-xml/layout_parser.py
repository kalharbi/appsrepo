import os.path
import re
from lxml import etree
from xml.etree import ElementTree
from lxml.etree import ParserError
from lxml.etree import XMLSyntaxError
class LayoutParser(object):
    
    def __init__(self, log):
        self.log = log

    def start_parser(self, layout_file, apk_dir):
        root = None
        try:
            root = etree.parse(layout_file)
        except XMLSyntaxError:
            self.log.error('Invalid XML Syntax for %s', layout_file)
            return None
        except IOError:
            self.log.error('Failed to read layout file %s', layout_file)
            return None
        for child in root.iter():
            if child.tag == 'include':
                embeded_layout = child.get('layout')
                if embeded_layout is None:
                    d = dict(child.attrib)
                    for k,v in d.items():
                        if '/' in v and '@' in v:
                            pattern = re.match(r'@(.*?)/', v)
                            if pattern is not None:
                                dir_name = pattern.group(1)
                                if os.path.exists(os.path.join(apk_dir, 'res', dir_name)):
                                    embeded_layout = v
                                    break
                embeded_dir, embeded_file = embeded_layout[1:].split('/')
                embeded_file_full_path = os.path.join(apk_dir, 'res', embeded_dir, 
                                                      embeded_file + '.xml')
                # Get the tree of the included layout
                emebeded_tree = LayoutParser(self.log).parse(embeded_file_full_path,
                                                                apk_dir)
                if emebeded_tree is not None and child.getparent() is not None:
                    child.getparent().append(emebeded_tree.getroot())
                if child.getparent() is not None:
                    # Remove the include tag
                    child.getparent().remove(child)
            else:
                attributes = dict(child.attrib)
                for attr_name, attr_value in attributes.iteritems(): 
                    if '@' in attr_value:
                        pattern = re.match(r'@(.*?)/', attr_value)
                        if pattern is None:
                            continue
                        res_element = pattern.group(1)
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
    def find_attr_value(self, xml_file, element_name, attribute_name):
        try:
            if not os.path.exists(xml_file):
                self.log.warning('Warning: Resource file %s does not exist, ', xml_file)
                return []
            tree = etree.parse(xml_file)
            if attribute_name is not None:
                xpath_query = "//" + element_name + '[@name="' + attribute_name + '"]/text()'
                return tree.xpath(xpath_query,
                  namespaces={'android': "http://schemas.android.com/apk/res/android"})
        except (ParserError, XMLSyntaxError) as e:
            self.log.error("XML parsing error occured while parsing file: %s", xml_file)
        return []
    
    def parse(self, layout_file, apk_dir):
        return self.start_parser(layout_file, apk_dir)
        
    