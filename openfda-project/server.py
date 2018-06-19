import http.server
import http.client
import json
import socketserver

# Puerto donde se lanza el servidor
PORT = 8000

# Clase derivada de BaseHTTPRequestHandler que hereda sus métodos.
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    API_URL = "api.fda.gov"
    API_EVENT = "/drug/event.json"
    API_DRUG = "&search=patient.drug.medicinalproduct:"
    API_COMPANY = "&search=companynumb:"

    # La función 'get_index' la utilizamos para definir el documento tipo html de la página principal de la aplicación.
    def get_index(self):
        index = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="utf-8">
                <title>Javi Martinez Project</title>
            </head>
            <body>
            <body style="background-color: lightgreen"></body>
            <p style="color:blue;font-size:50px;">OpenFDA Project</p>
            <form action = "listDrugs" method="get">
                <input type="submit" value="List Drugs">
                Limit: <input type="text" name="limit" value="10">
                </input>
            </form>
            <br>
            <br>
            <form action = "listCompanies" method="get">
                <input type="submit" value="Lists Companies">
                Limit: <input type="text" name="limit" value="10">
                </input>
            </form>
            <br>
            <br>
            <form action = "searchDrug" method="get">
                <input type="submit" value="Search Drug">
                : <input type="text" name="active_ingredient" value="">
                <br>
                Limit: <input type="text" name="limit" value="10">
                </input>
            </form>
            <br>
            <br>
            <form action = "searchCompany" method="get">
                <input type="submit" value="Search Company">
                : <input type="text" name="company" value="">
                <br>
                Limit: <input type="text" name="limit" value="10">
                </input>
            </form>
            <br>
            <br>
            <form action = "listWarnings" method="get">
                <input type="submit" value="List Warnings">
                Limit: <input type="text" name="limit" value="10">
                </input>
            </form>             
            </body>
            </html>"""
        return index

    # Esta función se activa cuando hay una petición GET.
    def do_GET(self):

        # Separamos la url por '?'.
        resource = self.path.split("?")

        if len(resource) > 1:
            parameters = resource[1]

        else:
            parameters = ""

        # Si hay 'parameters', los separamos por '&'.
        if parameters:
            array_parametros = parameters.split("&")
            parametros_nombrados = {}

            # Cada 'parameter' dentro de 'array_parametros' lo imprimimos a través de 'parametros_nombrados'.
            for unPar in array_parametros:
                parSplit = unPar.split("=")
                parametros_nombrados[parSplit[0]] = parSplit[1]
                print("Los parametros son: ", parametros_nombrados)

            # Ponemos el límite que se haya introducido.
            # Si no se introduce ninguno, se utiliza por defecto '10' como límite.
            if "limit" in parametros_nombrados:
                limit = int(parametros_nombrados["limit"])
                print("El limite es: " , limit)

            else:
                limit = 10

        # Si no hay 'parameters', se imprime esto.
        else:
            print("No hay parámetro")

        # Esta es la entrada índice.
        if self.path == '/':

            # Código de estado de respuesta
            self.send_response(200)
            # Enviamos la cabecera
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Contruye la aplicación como un string.
            index = self.get_index()
            self.wfile.write(bytes(index, "utf8"))

        # Petición de listado de fármacos
        elif 'listDrugs' in self.path:
            # Repetimos lo de entrada índice.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Abrimos la api de OpenFDA.
            conection = http.client.HTTPSConnection(self.API_URL)
            # Formamos la url.
            conection.request("GET", self.API_EVENT + "?limit=" + str(limit))
            # Recogemos la información en 'data'.
            data = conection.getresponse()
            # Leemos la información de 'data' y la decodificamos guardándola en 'repos'.
            raw = data.read().decode("utf8")
            # Pasamos la información a json
            repos = json.loads(raw)
            # Guardamos la información que nos interesa, la de 'results' en 'info'
            info = repos['results']
            drugs = []
            # Por cada elementod de 'info' añadimos a 'drugs' el que se encuentra en esa posición.
            for i in info:
                drugs += [i['patient']['drug'][0]['medicinalproduct']]

            # Este es el documento tipo html de 'listDrugs'.
            html = """
                <!DOCTYPE html>
                   <html lang="es">
                   <head>
                       <meta charset="utf-8">
                       <title>Javi Martinez List Drugs</title>
                   </head>
                   <body>
                   <body style="background-color: lightgreen"></body>
                   <p style="color:blue;font-size:50px;">List Drugs</p>
                   <ul>"""

            # Cada fármaco buscado e introducido en 'drugs' se añade al html para salir en la página.
            for obj in drugs:
                html += "<li>" + obj + "</li>"

            # Añadimos una forma cómoda de volver a la página principal de la aplicación.
            html += """
                                        </ul>
                                        <a href="/">Return</a>
                                    </body>
                                </html>"""

            self.wfile.write(bytes(html, "utf8"))

        # Repetimos los mismos pasos para la petición de la lista de empresas.
        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            conection = http.client.HTTPSConnection(self.API_URL)
            conection.request("GET", self.API_EVENT + "?limit=" + str(limit))
            data = conection.getresponse()
            raw = data.read().decode("utf8")
            repos = json.loads(raw)
            info = repos['results']
            company = []
            for i in info:
                company += [i['companynumb']]
            html = """
                        <!DOCTYPE html>
                           <html lang="es">
                           <head>
                               <meta charset="utf-8">
                               <title>Javi Martinez List Companies</title>
                           </head>
                           <body>
                           <body style="background-color: lightgreen"></body>
                           <p style="color:blue;font-size:50px;">List Companies</p>
                           <ul>"""

            for obj in company:
                html += "<li>" + obj + "</li>"

            html += """
                                </ul>
                                <a href="/">Return</a>
                            </body>
                        </html>"""

            self.wfile.write(bytes(html, "utf8"))

        # Repetimos los pasos también con la búsqueda de fármacos.
        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Añadimos el ingrdiente activo, dentro de 'parametros_nombrados' en este caso para la búsqueda
            # de los fármacos que lo lleven.
            farmaco = parametros_nombrados['active_ingredient']
            conection = http.client.HTTPSConnection(self.API_URL)
            conection.request("GET", self.API_EVENT + "?limit=" + str(limit) + self.API_DRUG + farmaco)
            data = conection.getresponse()
            raw = data.read().decode("utf-8")
            repos = json.loads(raw)
            info_search_drug = repos['results']
            drugs = {}
            indice = 0
            for i in info_search_drug:
                drugs[indice] = i['patient']['drug'][0]['medicinalproduct']
                indice += 1

            html = """
                        <!DOCTYPE html>
                            <html lang="es">
                            <head>
                               <meta charset="utf-8">
                               <title>Javi Martinez Search Drug</title>
                           </head>
                           <body>
                           <body style="background-color: lightgreen"></body>
                           <p style="color:blue;font-size:50px;">Results: </p>
                           <ul>"""

            for obj in drugs:
                html+=  "<li>" + drugs[obj] + "</li>"

            html+=  """
                                </ul>
                                <a href="/">Return</a>
                            </body>
                        </html>"""

            self.wfile.write(bytes(html, "utf-8"))

        # Repetimos los pasos también con la búsqueda de empresas
        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Añadimos la empresa, dentro de 'parametros_nombrados', en este caso.
            empresa = parametros_nombrados['company']
            conection = http.client.HTTPSConnection(self.API_URL)
            conection.request("GET", self.API_EVENT + "?limit=" + str(limit) + self.API_COMPANY + empresa)
            data = conection.getresponse()
            raw = data.read().decode("utf-8")
            repo = json.loads(raw)
            info_search_company = repo['results']
            company = {}
            indice = 0
            for i in info_search_company:
                company[indice] = [i['companynumb']]
                indice += 1

            html = """
                        <!DOCTYPE html>
                            <html lang="es">
                            <head>
                                <meta charset="utf-8">
                                <title>Javi Martinez Search Company</title>
                            </head>
                            <body>
                            <body style="background-color: lightgreen"></body>
                            <p style="color:blue;font-size:50px;">Results: </p>
                            <ul>"""

            for obj in company:
                html += "<li>" + str(company[obj]) + "</li>"

            html += """
                                            </ul>
                                            <a href="/">Return</a>
                                        </body>
                                    </html>"""

            self.wfile.write(bytes(html, "utf8"))

        # Volvemos a repetir los pasos por última vez, para la lista de advertencias.
        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            conection = http.client.HTTPSConnection(self.API_URL)
            conection.request("GET", self.API_EVENT + "?limit=" + str(limit))
            data = conection.getresponse()
            raw = data.read().decode("utf8")
            repos = json.loads(raw)
            info = repos['results']
            advertencias = []
            for i in info:
                if 'warnings' in i:
                    advertencias.append(i['warnings'][0])
                else:
                    advertencias.append("No warning")

            html = """
                    <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="utf-8">
                            <title>Javi Martinez List Warnings</title>
                        </head>
                        <body>
                        <body style="background-color: lightgreen"></body>
                        <p style="color:blue;font-size:50px;">List Warnings: </p>
                        <ul>"""

            for obj in advertencias:
                html += "<li>" + obj + "</li>"

            html += """
                                </ul>
                                <a href="/">Return</a>
                            </body>
                        </html>"""

            self.wfile.write(bytes(html, "utf8"))

        # Vuelve a la página principal de la aplicación.
        elif "redirect" in self.path:
            self.send_response(301)
            self.send_header("Location", "http://localhost:" + str(PORT))
            self.end_headers()

        # Implementamos el error '401'.
        elif "secret" in self.path:
            self.send_error(401)
            self.send_header("www-Aunthenticate", "Basic real")
            self.end_headers()

        # Implementamos el error '404: recurso no encontrado'.
        else:
            self.send_error(404)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Recurso no encontrado '{}'.".format(self.path).encode())

        return


socketserver.TCPServer.allow_reuse_address = True

# Atiende a las peticiones HTTP de los clientes.
Handler = testHTTPRequestHandler

# Asocia una IP y un puerto, configurando el socket del servidor, esperando las conexiones de los clientes.
httpd = socketserver.TCPServer(("", PORT), Handler)
print("Sirviendo en el puerto", PORT)

# Se utiliza para arrancar el servidor
httpd.serve_forever()
