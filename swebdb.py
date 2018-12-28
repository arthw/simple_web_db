#!/usr/bin/python3
import sys
import logging
import cgi

from http.server import SimpleHTTPRequestHandler
import socketserver
import json
import pickle


db = {}
config = {"data_file": "swebdb.pkl"}

class SimpleWebDB(SimpleHTTPRequestHandler):
    def _set_headers(self, ctype="html"):
        self.send_response(200)
        if ctype == "html":
            ctype = "text/html"
        elif ctype == "json":
            ctype = "application/json"
        else:
            ctype = "text/html"

        self.send_header('Content-type', ctype)
        self.end_headers()
    def header(self):
        return '''
<head>
<style type="text/css">
h1 {text-align: center;}
h2 {color:;}
p {margin-left: 20px}
body {background-color: #25772d; color: #ececec;}
</style>
</head>
'''

    def create_index(self, key, val):
        html = '''
<html>%s
<body>
<h1 >Simple Web Database</h1>
<hr/>
<h2>Search and Modify/Insert</h2>
<form action="gui" method="post">
Key:<br>
<input type="text" name="key" value="%s">
<br>
Value:<br>
<input type="text" name="val" value="%s">
<br><br>
<input type="submit" value="Save" name="save">
<input type="submit" value="Query" name="query">
</form>
</body></html>
''' % (self.header(), key, val)
        return str.encode(html)

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self.create_index("key", "value"))

    def write_data(self, key, val):
        db[key] = val
        save_data(db)

    def handle_query_save(self, op, key, val):
        if op == "query":
            cur_val = db.get(key, "")
            val = cur_val
        else:
            self.write_data(key, val)

        return key, val

    def decode_form(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
            })
        return form

    def handle_gui(self):
        form = self.decode_form()
        self._set_headers()
        key = form.getvalue('key')
        val = form.getvalue('val')
        if form.getvalue("query"):
            op = "query"
        else:
            op = "save"

        key, val = self.handle_query_save(op, key, val)
        self.wfile.write(self.create_index(key, val))

    def handle_api(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length).decode("utf-8"))

        key = message.get('key')
        val = message.get('val')
        op = message.get('op')
        if not key or not op:
            self.send_response(400)
            self.end_headers()
            return 
        key, val = self.handle_query_save(op, key, val)
        message['val'] = val
        self._set_headers("json")
        logging.warn("return %s" % str(message))
        self.wfile.write(json.dumps(message).encode())
       
    def do_POST(self):
        if self.path == '/api':
            self.handle_api()
        else:
            self.handle_gui()

def load_data():
    global db
    filename = config['data_file']
    try:
        with open(filename, "rb" ) as f:
            db = pickle.load(f)
    except:
        #print("Unexpected error:", sys.exc_info()[0])
        print("No existed %s, Database is empty" % filename)

def save_data(cur_db):
    with open( config['data_file'], "wb" ) as f:
        pickle.dump(cur_db, f, pickle.HIGHEST_PROTOCOL)

def run(handler_class=SimpleWebDB, port=80):
    load_data()
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", port), handler_class)
    print('Starting httpd...')
    httpd.serve_forever()


if __name__=="__main__":
    run(SimpleWebDB, 8002)
