class PathPermission(object):
    def __init__(self, path, pathPrefix, pathPattern, permission,
                 readPermission, writePermission):
        self.path = path
        self.pathPrefix = pathPrefix
        self.pathPattern = pathPattern
        self.permission = permission
        self.readPermission = readPermission
        self.writePermission = writePermission
        
        def get_path(self):
            return self.path
            
        def get_pathPrefix(self):
            return self.pathPrefix
        
        def get_pathPattern(self):
            return self.pathPattern
            
        def get_permission(self):
            return self.permission
            
        def get_readPermission(self):
            return self.readPermission
        
        def get_writePermission(self):
            return self.writePermission
