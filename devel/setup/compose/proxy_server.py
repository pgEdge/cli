import http.server
import socketserver
import os
import urllib.request
import argparse


class ProxyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - %s" % (self.client_address[0], format % args))
        
    def do_GET(self):
        """Serve file if it exists locally, otherwise proxy the request."""
        path_parts = self.path.lstrip("/").split("/")
        if len(path_parts) < 2:
            self.send_error(
                400, "Bad Request: URL must include a repository and a file path"
            )
            return

        repo = path_parts[0]
        if repo not in ["devel", "upstream", "download"]:
            self.send_error(400, "Bad Request: Invalid repository")
            return

        local_path = os.path.join(os.getcwd(), *path_parts[1:])
        if os.path.exists(local_path) and os.path.isfile(local_path):
            self.log_message("Fatching local file: %s", local_path)
            self.path = "/" + "/".join(path_parts[1:])
            return super().do_GET()
        else:
            remote_path = "/".join(path_parts[1:])
            self.log_message("Fatching remote file: %s", remote_path)
            self.proxy_request(repo, remote_path)

    def proxy_request(self, repo, path):
        """Fetch content from the upstream server and send it to the client."""
        upstream_url = f"https://pgedge-{repo}.s3.amazonaws.com/REPO/{path}"
        self.log_message("Proxying request to %s", upstream_url)
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
    parser = argparse.ArgumentParser(
        description="Start a simple proxy server with local file serving."
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=os.getcwd(),
        help="Local directory to serve files from",
    )

    args = parser.parse_args()

    os.chdir(args.directory)  # Change directory before starting the server

    with socketserver.TCPServer(("", args.port), ProxyRequestHandler) as httpd:
        print(f"Serving on port {args.port}, serving files from {args.directory}")
        httpd.serve_forever()
