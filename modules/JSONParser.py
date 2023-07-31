class JSONParser:
    def __init__(self):
        pass

    #main parse function
    def parse(self, data):
        return self.parseObject(data)
    
    #parse a single json object
    #Called recursively to parse nested objects
    def parseObject(self, data):
        if data[0] == '{' and data[-1] == '}':
            return self.parsePairs(data[1:-1])
        else:
            return data
        
    #parse a list of key value pairs
    #Called recursively to parse nested objects
    def parsePairs(self, data):
        splits = data.split(',')
        list_of_maps = []
        key_value_pairs = {}
        for split in splits:
            list_of_maps.append(self.parsePair(split))
        for map in list_of_maps:
            for key in map:
                key_value_pairs[key] = map[key]
        return key_value_pairs
    
    #parse a single key value pair
    #Called recursively to parse nested objects
    def parsePair(self, data):
        splits = data.split(':',1)
        if(len(splits) != 2):
            return {splits[0]:''}
        key = splits[0].strip().replace('"','')
        value = splits[1].strip().replace('"','')
        value = self.parseObject(value)
        return {key:value}

        