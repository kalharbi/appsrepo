import pandas as pd
import re
import os
from lxml import etree as ET

def get_immediate_subdirectories(a_dir):
  return [name for name in os.listdir(a_dir)
    if os.path.isdir(os.path.join(a_dir, name))]

def parse_xml(name, path, results_df, layouts):
  tree = ET.parse(path)
  m = re.search('^([^-]+)-([^-]+)', name)
  app = tree.xpath('//App')
  directory = 0
  files = 0
  layout = 0
  #Layour
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



### Main ###
xml_path = "../../science/health-apps/unpacked/"
layouts = ['LinearLayout', 'RelativeLayout', 'TableLayout', 'AbsoluteLayout', 'FrameLayout', 'ListView', 'GridView']
results_df = pd.DataFrame(columns = ['package', 'verc', 'app_nodes', 'directory_nodes', 'file_nodes', 'layout_nodes'])
results_df.set_index(['package', 'verc'], inplace = True)

sub_dirs = get_immediate_subdirectories(xml_path)
for sub_dir in sub_dirs:
  path = xml_path + sub_dir + "/ui-xml/" + sub_dir + ".xml"
  results_df = parse_xml(sub_dir, path, results_df, layouts)

f = open('test.csv', 'wb')
f.write(results_df.to_csv())
f.close()
