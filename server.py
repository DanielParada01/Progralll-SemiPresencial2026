from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import crud_usuarios

import json

port = 3000
crudUsuarios = crud_usuarios.crud_usuarios()

class miServidor(SimpleHTTPRequestHandler):
    def do_POST(self):
        urlParse = urlparse(self.path)
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = json.loads(datos)

        self.send_response(200)
        self.send_header("Content-type","application/json")
        self.end_headers()

        if urlParse.path == "/login":
            respuesta = {'msg': crudUsuarios.login(datos)}
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

        elif urlParse.path == "/usuario":
            respuesta = {'msg': crudUsuarios.crud_usuarios_usss091825(datos)}
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)

        if urlParse.path == "/usuarios":
            buscar = qs.get('buscar', [''])[0]
            datos = crudUsuarios.consultar(buscar)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))

        elif urlParse.path == "/":
            self.path = "/login.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

print(f"Servidor corriendo en el puerto {port}")
server = HTTPServer(("localhost",port),miServidor)
server.serve_forever()
