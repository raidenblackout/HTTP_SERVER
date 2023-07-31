# HTTP Server

This is a simple HTTP server implemented in Python using sockets. It provides a basic framework for handling GET and POST requests with custom routes and serving static files.

## Getting Started

To use this HTTP server, follow these steps:

1. Import the HTTPServer class from modules.HTTPServer
```python
from modules.HTTPServer import HTTPServer
```
2. Create a new instance of the HTTPServer class
```python
server = HTTPServer('localhost', 8080)
```
3. Create callback functions for each route you want to handle
```python
def index(request, response):
    response.set_body(b'Hello, World!')
    response.send()

def about(request, response):
    response.set_body(b'About page')
    response.send()

def forbidden(request, response):
    response.status(403).send(custom = b'Forbidden')
```
4. Add the routes to the server
```python
server.get('/',callback=index)
server.get('/about',callback=about)
server.get('/forbidden',callback=forbidden)
```
5. Start the server
```python
server.run()
```

Once the server is running, navigate to http://localhost:8080 in your web browser to access the custom route for GET requests. For POST requests, you can use appropriate tools like curl or HTML forms.

# Features
### 1. Request Handling
The server can handle incoming client requests. It parses the request and creates a corresponding Request object.

### 2. Response Handling
The server creates a Response object to construct the response and sends it back to the client.

### 3. Routing
You can add custom routes for GET and POST requests using the get() and post() methods, respectively.

### 4. Serving Static Files
The server is capable of serving static files located in the specified root directory.

### 5. Logging
The server logs incoming requests and responses to a file specified during initialization.

### Example
```python
from http_server import HTTPServer

def handle_get_request(request, response):
    response.status(200).send(b"Hello, World!")
    

def handle_post_request(request, response):
    # Custom logic to handle POST requests
    # ...
    pass

if __name__ == "__main__":
    server = HTTPServer('localhost', 8080)
    server.get('/', handle_get_request)
    server.post('/submit', handle_post_request)
    server.get('/static', root_dir = 'static')
    server.run()
```

## License

This project is licensed under the [MIT License](LICENSE).
