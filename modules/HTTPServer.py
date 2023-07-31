import socket
from threading import Thread
from modules.Request import Request
from modules.Trie import Trie
from modules.Response import Response
from modules.Logger import Logger
import os
class HTTPServer:
    #initialization of the server
    def __init__(self,host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host,self.port))
        self.keyPress =''
        self.client_thread_list = []
        self.client_list = []
        self.post_routes = Trie()
        self.get_routes = Trie()
        self.logger = Logger('logs.txt')
    
    #handle client request
    def handleClient(self, client, address):
        self.client_list.append(client)
        #check if the q key is pressed
        while self.keyPress != 'q':
            #reset the timeout
            client.settimeout(100)
            data= b''
            #receive the data from client
            while b'\r\n\r\n' not in data:
                try:
                    data += client.recv(1024)
                except:
                    break
                if data == b'' or self.keyPress == 'q':
                    break

            #check if the connection is closed
            if data == b'':
                break

            #parse the request
            request = Request(data.decode())
            self.logger.log(data.decode(), 'REQUEST', str(address[0])+':' + str(address[1]))

            #create a response object
            response = Response(client)

            #handle the request and send the response
            self.handleRequest(request, response, address)
        self.logger.log("Connection closed", 'INFO', str(address[0])+':' + str(address[1]))
        client.close()

    #run the server
    def run(self):
        print("Server is listening on port ", self.port)
        self.logger.log("Server is listening on port "+ str(self.port))
        self.socket.listen(5)

        #start listening and handle incoming connections
        main_thread = Thread(target=self.listen)
        main_thread.start()

        #check if the q key is pressed
        while self.keyPress != 'q':
            self.keyPress = input("Press q to quit\n")

        #close the server
        self.socket.close()

        #close all the client connections
        for client in self.client_list:
            client.close()

        #wait for all the threads to finish
        for client_thread in self.client_thread_list:
            client_thread.join()
        main_thread.join()
        self.logger.stop()

    #listen for incoming connections
    def listen(self):
        #check if the q key is pressed
        while self.keyPress != 'q':
            try:
                #accept incoming connections
                client, address = self.socket.accept()
                print("Connected to ", address)
                self.logger.log("Connected to "+ str(address))

                #create a thread to handle the client
                client_thread = Thread(target=self.handleClient, args=(client,address))
                client_thread.start()

                #add the thread to the list to keep track of it
                self.client_thread_list.append(client_thread)
            except KeyboardInterrupt:
                break
            except:
                break
    
    #handle a single request
    def handleRequest(self, request, response,address):
        path= request.path.split('/')

        #for uniquely identifying the root path * has been used as path.split('/') returns an empty string for the first element
        #so the path /path/to/file will be ['*','path','to','file'] and the path / will be ['*']
        path[0] = '*'
        if request.method == 'GET':
            #check the route for the longest matching path and get the callback function
            callback = self.get_routes.search(path)

            #if the callback is not None then call the callback function else send a 404 response
            if callback != None:
                callback(request, response)
            else:
                response.status = '404'
                response.message = 'Not Found'

        elif request.method == 'POST':
            #check the route for the longest matching path and get the callback function
            callback = self.post_routes.search(path)

            #if the callback is not None then call the callback function else send a 404 response
            if callback != None:
                callback(request, response)
            else:
                response.status = '404'
                response.body = [b'Not Found', 'text/html']
        #if the method is not GET or POST then send a 405 response
        else:
            response.status = '405'
            response.message = 'Method Not Allowed'
            response.body = [b'Method Not Allowed', 'text/html']
        
        self.logger.log(str(response), 'RESPONSE', str(address[0])+':' + str(address[1]))
    
    #function for handling urls such as localhost:8080/path (not localhost:8080/path/)
    def isFilePath(self, path):
        if path[-1] == '/':
            return True
        for i in path[::-1]:
            if i == '.':
                return True
            elif i == '/':
                return False
        return False

    #add a route for POST requests
    def post(self, path, callback=None, root_dir = None):
        temp_path=  path  
        if root_dir != None:
            #default callback function if no callback is provided
            def callback_func(request, response):
                if self.isFilePath(request.path) == False:
                    res = (
                            "HTTP/1.1 302 Found\r\n"
                            f"Location: {request.path+'/'}\r\n"
                            "Connection: close\r\n"
                            "\r\n"
                            )
                    response.send(custom=res)
                    return
                try:
                    response.set_body(self.getFile(request.path, root_dir, temp_path))
                except:
                    response.set_body(b'File not found')
                    response.set_status('404')
                    response.set_message('Not Found')
            callback = callback_func
        if path == '/':
            path = ['*']
        else :
            path = path.split('/')
            path[0] = '*'
            #inserting the path in the trie along with the callback function
        self.post_routes.insert(path, callback)

    #add a route for GET requests
    def get(self, path, callback=None, root_dir = None):
        temp_path=  path    
        if root_dir != None:
            #default callback function if no callback is provided
            def callback_func(request, response):
                if self.isFilePath(request.path) == False:
                    res = (
                            "HTTP/1.1 302 Found\r\n"
                            f"Location: {request.path+'/'}\r\n"
                            "Connection: close\r\n"
                            "\r\n"
                            )
                    response.send(custom=res)
                    return
                    
                try:
                    file_data = self.getFile(request.path, root_dir, temp_path)
                    response.set_body(file_data[0], file_data[1])
                except Exception as e:
                    response.set_body(b'File not found')
                    response.set_status('404')
                    response.set_message('Not Found')
                response.send()
            callback = callback_func
        if path == '/':
            #as mentioned earlier * is used to uniquely identify the root path
            path = ['*']
        else :
            path = path.split('/')
            #as mentioned earlier * is used to uniquely identify the root path
            path[0] = '*'

        #inserting the path in the trie along with the callback function
        self.get_routes.insert(path, callback)

    #check if dir exists
    def checkPath(self,path, root_dir):
        full_path = root_dir + path
        if os.path.exists(full_path):
            return True
        else:
            return False
        
    #get the MIME type
    def getFileType(self, path):
        splits = path.split('.')
        if len(splits) == 1:
            return 'text/html'
        elif splits[-1] in ['html', 'css', 'js']:
            return 'text/'+splits[-1]
        elif splits[-1] in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image/'+splits[-1]
        elif splits[-1] in ['mp4', 'avi', 'mkv', 'mov']:
            return 'video/'+splits[-1]
        elif splits[-1] in ['mp3', 'wav', 'ogg']:
            return 'audio/'+splits[-1]
        elif splits[-1] in ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']:
            return 'application/'+splits[-1]
        elif splits[-1] in ['ttf', 'otf', 'woff', 'woff2'] :
            return 'font/'+splits[-1]
        else:
            return 'application/octet-stream'
    
    #get file data in binary
    def getFile(self, path, root_dir, endpoint):
        temp_path=path
        if endpoint != '/':
            temp_path = temp_path.replace(endpoint, '')
        directory = ''
        #check if file exists
        if self.checkPath(temp_path, root_dir):
            #builds the path to the file
            directory = root_dir + temp_path
        else:
            raise Exception('File not found')
        
        #if the path is a directory then add index.html to the path
        if os.path.isdir(directory):
            directory += '/index.html'
        
        #read the file and return the data in binary
        with open(directory, 'rb') as file:
            return (file.read(), self.getFileType(directory))



