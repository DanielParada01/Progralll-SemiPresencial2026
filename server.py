from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse 
from urllib.parse import urlparse, parse_qs
import crud_clientes
import crud_impuestos # NUEVO IMPORT

import json

port = 3000
crudClientes = crud_clientes.crud_clientes()
crudImpuestos = crud_impuestos.crud_impuestos() # NUEVA INSTANCIA

class miServidor(SimpleHTTPRequestHandler):
    def do_POST(self):
        urlParse = urlparse(self.path)
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = parse.unquote(datos)
        datos = json.loads(datos)
        
        self.send_response(200)
        self.send_header("Content-type","application/json")
        self.end_headers()

        if urlParse.path == "/cliente":
            respuesta = {'msg': crudClientes.administrar(datos)}
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))
            
        elif urlParse.path == "/guardar_periodo":
            respuesta = {'msg': crudImpuestos.guardar_periodo(datos)}
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)
       
        if urlParse.path == "/clientes":
            buscar = qs.get('buscar', [''])[0]
            datos = crudClientes.consultar(buscar)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))
            
        # RUTAS NUEVAS PARA IMPUESTOS
        elif urlParse.path == "/calcular_impuesto":
            balance = qs.get('balance', ['0'])[0]
            producto = qs.get('producto', ['11801'])[0]
            datos = crudImpuestos.calcular_impuesto(float(balance), producto)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))
            
        elif urlParse.path == "/periodos":
            idCliente = qs.get('idCliente', ['0'])[0]
            datos = crudImpuestos.consultar_periodos(idCliente)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))
        
        elif self.path == "/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

print(f"Servidor corriendo en el puerto {port}")
server = HTTPServer(("localhost",port),miServidor)
server.serve_forever()