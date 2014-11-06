class IntentFilter(object):
    def __init__(self, name, icon, label, priority):
        self.name = name
        self.icon = icon
        self.label = label
        self.priority = priority
        self.category = None
        self.data = []
        self.action = []
        
    def get_name(self):
        return self.name
        
    def get_icon(self):
        return self.icon
    
    def get_label(self):
        return self.label
        
    def get_priority(self):
        return self.priority
    
    def get_category(self):
        return self.category
        
    def set_category(self, name):
        self.category = name
         
    def get_data(self):
        return self.data
    
    def get_action(self):
        return self.action

    def set_data(self, scheme, host, port, path, pathPattern, pathPrefix,
                 mimeType):
        data_set = {'scheme': scheme, 'host': host, 'port': port, 'path': path,
                    'pathPattern': pathPattern,
                    'pathPrefix': pathPrefix, 'mimeType': mimeType}
        self.data.append(data_set)

    def set_action(self, name):
        action_set = {'name': name}
        self.action.append(action_set)
