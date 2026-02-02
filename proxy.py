import http.server
import urllib.request
import urllib.error
import os

os.chdir(r"C:\Users\Extreme\reality-transformer-local")

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy('GET')
        elif self.path == '/':
            self.path = '/Claude_HTML.html'
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy('POST')

    def proxy(self, method):
        url = f"http://localhost:8000{self.path}"
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else None
            req = urllib.request.Request(url, data=body, method=method)
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for h, v in resp.getheaders():
                    if h.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(h, v)
                self.end_headers()
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except urllib.error.URLError as e:
            self.send_error(502, str(e))

print("Serving Claude_HTML.html at http://localhost:5173")
print("Proxying /api/* to http://localhost:8000")
http.server.HTTPServer(('', 5173), ProxyHandler).serve_forever()
