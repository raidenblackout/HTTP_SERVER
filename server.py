from modules.HTTPServer import HTTPServer
server = HTTPServer('0.0.0.0', 8080)
server.get('/', root_dir='static')
server.get('/another', root_dir='test2')
def index(req, res):
    res.set_body(b'<h1>hello world</h1>')
    res.send()
server.post('/test', callback=index)
server.run()