# define ER manager class

# define html template for display


import json
import http.server
import socketserver
import threading
from pydantic import BaseModel
from pydantic.version import VERSION as P_VERSION

PYDANTIC_VERSION = P_VERSION
PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

def _get_keys_v1(kls):
    return kls.__fields__.keys()


def _get_keys_v2(kls):
    return kls.model_fields.keys()


get_keys = _get_keys_v2 if PYDANTIC_V2 else _get_keys_v1


PORT = 8001

# 定义 HTML 内容
# read content from ./index.html
with open('./er_explorer/index.html', 'r') as f:
    HTML_TEMPLATE = f.read()

def process_definitions(definitions):
    counter = 1

    node_map = {}
    nodes = []
    edges = []

    def get_desc(kls):
        name = kls.__name__
        keys = get_keys(kls)
        keys = '\n'.join(['- ' + k for k in keys])
        keys = '\n\n' + keys
        return f"<b>{name}</b>{keys}"

    for d in definitions:
        source = d['source']
        target = d['target']
        source_name = source.__name__
        target_name = target.__name__
        field = d['field']

        font = {
            'font': {'multi': 'html', 'align': 'left'},
            'shape': 'box',
            'color': '#fff', 
        }

        if source_name not in node_map:
            node_map[source_name] = counter
            counter += 1
            nodes.append({ 'id': node_map[source_name], 'label': get_desc(source), **font })

        if target_name not in node_map:
            node_map[target_name] = counter
            counter += 1
            nodes.append({ 'id': node_map[target_name], 'label': get_desc(target), **font })
        
        edges.append({ 
            'from': node_map[source_name],
            'to': node_map[target_name],
            'label': field,
            'physics': { 'springLength': 100 },
            'arrows': { 'to': { 'enabled': True, 'type': 'arrow', 'scaleFactor': 0.4 }} })

    data = {
        'nodes': nodes,
        'edges': edges,
    }
    return data


def serve(definitions):
    data = process_definitions(definitions)
    class MyRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path == '/':
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

                elif self.path == '/api/data':
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode('utf-8'))

                else:
                    self.send_error(404, "File Not Found")
            except BrokenPipeError:
                self.send_error(500, 'borken pipeline')

    Handler = MyRequestHandler
    class ReusableTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    httpd = ReusableTCPServer(("", PORT), Handler)

    shutdown_event = threading.Event()

    def control_thread_t():
        input("Press Enter to shutdown the server...\n")
        shutdown_event.set()
        httpd.shutdown()
        httpd.server_close()
        print('port released')
    print(f"Serving at port {PORT}")

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    control_thread = threading.Thread(target=control_thread_t)
    control_thread.start()
    server_thread.join()
