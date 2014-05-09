class PathPermission(object):

    def __init__(self, path, pathPrefix, pathPattern, permission, readPermission, writePermission):
        self.path = path
        self.pathPrefix = pathPrefix
        self.pathPattern = pathPattern
        self.permission = permission
        self.readPermission = readPermission
        self.writePermission = writePermission

