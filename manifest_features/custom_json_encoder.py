from json import JSONEncoder


class CustomJsonEncoder(JSONEncoder):
    def remove_none(self, data):
        if isinstance(data, dict):
            return {key: self.remove_none(value) for key, value in data.items()
                    if key and value}
        elif isinstance(data, list):
            return [self.remove_none(item) for item in data if item]
        elif isinstance(data, set):
            return {self.remove_none(item) for item in data if item}
        else:
            return data

    def default(self, obj):
        return self.remove_none(obj.__dict__)
