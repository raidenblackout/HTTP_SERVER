class Response:
    #status codes
    code_maps = {
        '200': 'OK',
        '201': 'Created',
        '202': 'Accepted',
        '204': 'No Content',
        '301': 'Moved Permanently',
        '302': 'Found',
        '304': 'Not Modified',
        '400': 'Bad Request',
        '401': 'Unauthorized',
        '403': 'Forbidden',
        '404': 'Not Found',
        '405': 'Method Not Allowed',
        '500': 'Internal Server Error',
        '501': 'Not Implemented',
        '502': 'Bad Gateway',
        '503': 'Service Unavailable'
    }

    def __init__(self, client, status = '200', message = 'OK', body = [b'', 'text/html']):
        self.client = client
        self.code = status
        self.message = message
        self.body = body
        self.default_headers = {
            "Content-Type": "text/html",
            "Content-Length": len(self.body[0])
        }
    
    #set the response body
    def set_header(self, key, value):
        self.default_headers[key] = value

    #set the response body
    def set_body(self, body, type = 'text/html'):
        self.body = [body, type]
        self.default_headers["Content-Length"] = len(self.body[0])
    
    #set the response status
    def set_status(self, status):
        self.code = status
    #set the response message
    def set_message(self, message):
        self.message = message

    #set the response data
    def set_data(self, data):
        self.data = data
    
    #set the status code and message and return the response object
    def status(self,status, message = None):
        self.code = str(status)
        if message != None:
            self.message = message
        else:
            self.message = Response.code_maps[self.code]
        return self
    
    #send the response to the client
    def send(self, custom = None):
        # print(custom)
        if custom == None:
            data = self.protocol().encode() + self.headers(content_type=self.body[1]).encode()  + self.body[0]
            # print(data)
            try:
                self.client.sendall(data)
            except:
                pass
        else:
            self.client.sendall(custom.encode())
    def __str__(self):
        data = self.protocol() + self.headers(content_type=self.body[1]) 
        return data
    
    #get the protocol string
    def protocol(self):
        return "HTTP/1.1 " + self.code + " " + self.message + "\r\n"
    
    #get the headers string
    def headers(self, content_type = None, args = None):
        headers = ""
        for key in self.default_headers:
            if content_type != None and key == "Content-Type":
                headers += key + ": " + content_type + "\r\n"
            else:
                headers += key + ": " + str(self.default_headers[key]) + "\r\n"
        return headers + "\r\n"
    
    #set a value for a header
    def setHeader(self, header, value):
        self.default_headers[header] = value

    