import logging
from query_manifest import QueryManifest

class QueryExecutor(object):
    
    manifest_features = ['permissions']
    
    @staticmethod
    def execute(query_dict):
        package_name = query_dict['package_name']
        version_index = query_dict['version_index']
        features = query_dict['features']
        functions = query_dict['functions']
        
        # Determine the collection type
        if features[0] in QueryExecutor.manifest_features:
            QueryManifest().execute_query(package_name, version_index, features, functions)
        else:
            logging.error("Undefined feature:  '%s' is not defined.", features[0])
    

        