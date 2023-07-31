from modules.JSONParser import JSONParser
        
class Request:
    def __init__(self,data):
        self.method = ''
        self.path = ''
        self.protocol = ''
        self.headers = {}
        self.body = ''
        self.data = data
        self.params = {}
        self.boundary = ''
        self.jsonParser = JSONParser()
        self.parse()
    
    #parse the request
    def parse(self):
        temp = self.data.split('\r\n\r\n')
        lines = temp[0].split('\r\n')
        body = ''
        for i in range(1,len(temp)):
            body += temp[i]+ '\r\n\r\n'
        lines.append(body)
        self.parseRequestLine(lines[0])
        self.parseHeaders(lines[1:-1])
        self.parseBody(lines[-1])
        self.parseParams()
        self.parseBoundary()

    #parse the method path and protocol
    def parseRequestLine(self, line):
        try:
            self.method, self.path, self.protocol = line.split(' ')
        except:
            self.method = ''
            self.path = ''
            self.protocol = ''
        self.method = self.method.strip()
        self.path = self.path.strip()
        self.protocol = self.protocol.strip()

    #parse the headers
    def parseHeaders(self, lines):
        for line in lines:
            if line == '':
                break
            splits= line.split(':')
            if len(splits) == 2:
                key = splits[0].strip().lower()
                value = splits[1].strip()
            else:
                key = splits[0].strip().lower()
                value = ''
                for i in range(1,len(splits)):
                    value += splits[i]
            self.headers[key] = value.strip()

    #parse the body
    def parseBody(self, line):
        self.body = line
        # print(self.headers)
        if 'content-type' in self.headers:
            if self.headers['content-type'].strip() == 'application/json':
                self.body = self.jsonParser.parse(self.body)
            elif self.headers['content-type'].strip() == 'application/x-www-form-urlencoded':
                self.parseUrlEncodedBody()
    
    #parse the url encoded body
    def parseUrlEncodedBody(self):
        params = self.body.split('&')
        for param in params:
            key_value = param.split('=')
            if len(key_value) == 2:
                self.params[key_value[0].strip()] = key_value[1].strip()
    
    #parse the params
    def parseParams(self):
        params = self.path.split('?')
        if len(params) == 2:
            self.path = params[0]
            params = params[1].split('&')
            for param in params:
                key_value = param.split('=')
                if len(key_value) == 2:
                    self.params[key_value[0]] = key_value[1]
    #parse the boundary
    def parseBoundary(self):
        if 'content-type' in self.headers:
            if 'multipart/form-data' in self.headers['content-type']:
                self.boundary = self.headers['content-type'].split('boundary=')[1]
                self.headers['content-type'] = 'multipart/form-data'
                self.parseMultipartBody()
    #parse the multipart body of html form
    def parseMultipartBody(self):
        if self.boundary != '':
            body = self.body.split('--'+self.boundary)
            for i in range(1,len(body)-1):
                self.parseMultipartBodyPart(body[i])
    
    #parse a single part of the multipart body
    def parseMultipartBodyPart(self, body):
        body = body.split('\r\n\r\n')
        headers = body[0].split('\r\n')
        if len(body) == 1:
            body = ''
        else:
            body = body[1].strip()
        key = ''
        for header in headers:
            if 'Content-Disposition' in header:
                key = header.split('name="')[1].split('"')[0].strip()
        self.params[key] = body
        self.body = ''

    def __str__(self):
        return "headers: "+self.headers.__str__()+ "\nbody: "+ self.body.__str__()+"\nmethod: "+ self.method.__str__()+"\npath: "+ self.path.__str__()+"\nprotocol: "+ self.protocol.__str__() + "\nparams: "+ self.params.__str__() + "\nboundary: "+ self.boundary.__str__()
