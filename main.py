from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import socket
import json
from time import sleep
from datetime import datetime
import threading

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        with socket.socket() as so:
            while True:
                try:
                    so.connect(('127.0.0.1', 5000))
                    so.sendall(data)
                    break
                except ConnectionRefusedError:
                    sleep(0.5)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def dict_server(host, port):
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data_parse = urllib.parse.unquote_plus(data.decode())
                print(data_parse)
                data_dict1 = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
                print(f'{data_dict1} no date')
                curDT = datetime.now()
                dt_now = curDT.strftime("%m-%d-%Y, %H:%M:%S.%f")
                data_dict2 = {dt_now: data_dict1}
                print(data_dict2)
                with open('storage/data.json', 'w', encoding="utf-8") as f:
                    json.dump(data_dict2, f)


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 5000

    server = threading.Thread(target=dict_server, args=(HOST, PORT))
    client = threading.Thread(target=run)

    server.start()
    client.start()
    server.join()
    client.join()
    print('Done!')
    
