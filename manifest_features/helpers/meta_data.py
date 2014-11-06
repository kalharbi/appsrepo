class MetaData(object):
    def __init__(self, name, resource, value):
        self.name = name
        self.resource = resource
        self.value = value
        
    def get_name(self):
        return self.name
        
    def get_resource(self):
        return self.resource
        
    def get_value(self):
        return self.value