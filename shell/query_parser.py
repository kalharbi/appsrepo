import re

class QueryParser(object):
    
    @staticmethod
    def explain(query_line):
        if not query_line:
            return None
        package_name = None
        version_index = None
        features = None
        functions = None
        
        # get package name
        package_pattern = re.compile('\((.*?)\)')
        package_match = package_pattern.match(query_line)
        if package_match is None:
            print('Invalid query: package name is missing. It must be embedded in parentheses.')
            return None
        else:
            package_name = package_match.group(1)
        
        # get version index
        remaining = query_line[package_pattern.search(query_line).end():]
        version_pattern = re.compile('\[(.*?)\]')
        version_match = version_pattern.search(remaining)
        if version_match is None:
            print('Invalid query: version index is missing. It must be embedded in square brackets.')
            return None
        else:
            version_index = int(version_match.group(1))
        
        # get features list
        remaining = query_line[version_pattern.search(query_line).end():]
        if not remaining.startswith('.'):
            print('Invalid query: feature name is missing. The version index must be followed by . and the feature name')
            return None
        else:
            remaining = remaining[1:].split('.')
            features = [x for x in remaining if not x.endswith(')')]
            if not features:
                print('Invalid query: feature name is missing.')
                return None
            functions = [x for x in remaining if x.endswith(')')] 
            if not functions:
                print('Invalid query: function is missing. A function must be specified to perform an action on the feature of the app.')
                return None
        explianed_query = {'package_name': package_name, 'version_index': version_index, 
                           'features':features, 'functions': functions}
        return explianed_query
        
        
        