import logging
from query_listing import QueryListing
from query_manifest import QueryManifest
from query_ui import QueryUI

class QueryExecutor(object):
    
    listing_features =['title', 'description', 'play_store_url', 
                'category', 'price', 'date_published', 'version_name',
                'version_code', 'operating_systems', 'ratings_count', 
                'rating', 'content_rating', 'creator', 'creator_url',
                'install_size', 'install_size_text', 'downloads_count',
                'downloads_count_text', 'reviews', 'permissions', 
                'what_is_new']
    
    manifest_features = ['uses_permissions','min_sdk_version', 'target_sdk_version',
                         'max_sdk_version', 'install_location', 'activities',
                         'uses_configurations', 'uses_features', 'supports_screens',
                         'compatible_screens', 'gl_texture', 'application',
                         'activities_aliases', 'services', 'receivers', 'providers',
                         'permissions', 'permission_trees', 'permission_groups',
                         'instrumentations', 'meta_data', 'uses_libraries']
    
    ui_features = ['layout', 'view', 'layout_files', 'layout_dirs']
    
    
    @staticmethod
    def execute(query_dict):
        package_name = query_dict['package_name']
        version_index = query_dict['version_index']
        features = query_dict['features']
        functions = query_dict['functions']
        
        # Determine the collection type
        if features[0] in QueryExecutor.listing_features:
            QueryListing().execute_query(package_name, version_index, features, functions)
        elif features[0] in QueryExecutor.manifest_features:
            QueryManifest().execute_query(package_name, version_index, features, functions)
        elif features[0] in QueryExecutor.ui_features:
            QueryUI().execute_query(package_name, version_index, features, functions)
        else:
            logging.error("Undefined feature:  '%s' is not defined.", features[0])
    

        