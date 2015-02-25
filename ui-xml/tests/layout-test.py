import pandas as pd
import re
import os
from lxml import etree as ET
import unittest
import sys
sys.path.append("/Users/Jackson/dev/appsrepo/ui-xml")
from ui_xml import UIXML

global trueAppNodes
global trueDirectoryNodes
global trueFileNodes

trueAppNodes = 1
trueDirectoryNodes = 10
trueFileNodes = 313

class TestSetup():
  def start(self, xml_path):
    UIXML().start_main(xml_path)
    layouts = ['LinearLayout', 'RelativeLayout', 'TableLayout', 'AbsoluteLayout', 'FrameLayout', 'ListView', 'GridView']
    results_df = pd.DataFrame(columns = ['package', 'verc', 'app_nodes', 'directory_nodes', 'file_nodes', 'layout_nodes'])
    results_df.set_index(['package', 'verc'], inplace = True)


    sub_dirs = self.get_immediate_subdirectories(xml_path)
    for sub_dir in sub_dirs:
      path = xml_path + sub_dir + "/ui-xml/" + sub_dir + ".xml"
      results_df = self.parse_xml(sub_dir, path, results_df, layouts)

    appNodes = results_df.loc[('com.endomondo.android', '120'), 'app_nodes']
    directoryNodes = results_df.loc[('com.endomondo.android', '120'), 'directory_nodes']
    fileNodes = results_df.loc[('com.endomondo.android', '120'), 'file_nodes']

    return appNodes, directoryNodes, fileNodes

  def get_immediate_subdirectories(self, a_dir):
    return [name for name in os.listdir(a_dir)
      if os.path.isdir(os.path.join(a_dir, name))]

  def parse_xml(self, name, path, results_df, layouts):
    tree = ET.parse(path)
    m = re.search('^([^-]+)-([^-]+)', name)
    app = tree.xpath('//App')
    directory = 0
    files = 0
    layout = 0
    #Layout
    for l in layouts:
      search = '//' + l
      layoutTag = tree.xpath(search)
      for i in layoutTag:
        for j in i.iterdescendants():
          layout += 1

    # App, Directory, and Files
    for appNode in app:
      directoryNodes = appNode.findall('Directory')
      directory += len(directoryNodes)
      for directoryNode in directoryNodes:
        fileNodes = directoryNode.findall('File')
        files += len(fileNodes)
    results_df.loc[(m.group(1), m.group(2)), 'app_nodes'] = len(app)
    results_df.loc[(m.group(1), m.group(2)), 'directory_nodes'] = directory
    results_df.loc[(m.group(1), m.group(2)), 'file_nodes'] = files
    results_df.loc[(m.group(1), m.group(2)), 'layout_nodes'] = layout
    return results_df

class UIXMLTest(unittest.TestCase):
  def __init__(self, testname, appNodes, directoryNodes, fileNodes):
    super(UIXMLTest, self).__init__(testname)
    self.appNodes = appNodes
    self.directoryNodes = directoryNodes
    self.fileNodes = fileNodes

  def test_appNode(self):
    true = trueAppNodes
    count = self.appNodes
    self.assertEqual(true, count)

  def test_directoryNode(self):
    true = trueDirectoryNodes
    count = self.directoryNodes
    self.assertEqual(true, count)

  def test_fileNode(self):
    true = trueFileNodes
    count = self.fileNodes
    self.assertEqual(true, count)


if __name__ == '__main__':
  appNodes, directoryNodes, fileNodes = TestSetup().start("/Users/Jackson/dev/appsrepo/ui-xml/tests/data/")
  suite = unittest.TestSuite()
  suite.addTest(UIXMLTest("test_appNode", appNodes, directoryNodes, fileNodes))
  suite.addTest(UIXMLTest("test_directoryNode", appNodes, directoryNodes, fileNodes))
  suite.addTest(UIXMLTest("test_fileNode", appNodes, directoryNodes, fileNodes))

  unittest.TextTestRunner().run(suite)
