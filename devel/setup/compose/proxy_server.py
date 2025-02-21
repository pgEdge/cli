import http.server
import socketserver
import os
import urllib.request
import argparse

UPSTREAM_SERVER = "https://pgedge-devel.s3.amazonaws.com/REPO"  # Change this to your target server
PORT = 8000

class ProxyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        
        """Serve file if it exists locally, otherwise proxy the request."""
        local_path = os.path.join(os.getcwd(), self.path.lstrip('/'))
        print(f"Local path: {local_path}")
        if os.path.exists(local_path) and os.path.isfile(local_path):
            return super().do_GET()
        else:
            self.proxy_request()

    def proxy_request(self):
        """Fetch content from the upstream server and send it to the client."""
        upstream_url = UPSTREAM_SERVER + self.path
        try:
            with urllib.request.urlopen(upstream_url) as response:
                self.send_response(response.status)
                for header in response.getheaders():
                    self.send_header(header[0], header[1])
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a simple proxy server with local file serving.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--directory", "-d", type=str, default=os.getcwd(), help="Local directory to serve files from")
    
    args = parser.parse_args()

    os.chdir(args.directory)  # Change directory before starting the server

    with socketserver.TCPServer(("", args.port), ProxyRequestHandler) as httpd:
        print(f"Serving on port {args.port}, serving files from {args.directory}")
        httpd.serve_forever()
