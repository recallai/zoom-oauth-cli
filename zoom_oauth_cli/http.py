from http.server import BaseHTTPRequestHandler, HTTPServer


def serve_token(port, token_callback):
    httpd = HTTPServer(("", port), ServeTokenCallbackHandler)
    httpd.token_callback = token_callback
    httpd.serve_forever()


class ServeTokenCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = self.server.token_callback()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(token.encode("utf-8"))
