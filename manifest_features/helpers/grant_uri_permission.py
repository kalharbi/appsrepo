class GrantUriPermission(object):
    def __init__(self, path, pathPattern, pathPrefix):
        self.path = path
        self.pathPattern = pathPattern
        self.pathPrefix = pathPrefix
        
    def get_path(self):
        return self.path
        
    def get_pathPrefix(self):
        return self.pathPrefix
    
    def get_pathPattern(self):
        return self.pathPattern
