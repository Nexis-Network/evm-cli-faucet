#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import subprocess
import threading

class S(BaseHTTPRequestHandler):
    # Ethereum address rate limiting storage
    address_timings = {}

    def _set_headers(self, status_code=200, content_type='text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        # Handle pre-flight requests for CORS
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        address = post_data.strip()

        # Check if the address is valid Ethereum address (simple validation)
        if len(address) == 42 and address.startswith('0x'):
            current_time = time.time()
            if address in self.address_timings and current_time - self.address_timings[address] < 300:
                self._set_headers(429)
                self.wfile.write(b"Too many requests. Please wait.")
                return

            self.address_timings[address] = current_time
            self._set_headers()

            # Start the Nexis command in a new thread
            thread = threading.Thread(target=self.run_nexis_command, args=(address,))
            thread.start()
            
            # Respond immediately to the client
            self.wfile.write(f"Command execution started for {address}".encode('utf-8'))
        else:
            self._set_headers(400)
            self.wfile.write(b"Invalid Ethereum address provided.")

    def run_nexis_command(self, address):
        """Run the nexis command asynchronously."""
        try:
            subprocess.run(["nexis", "evm", "transfer-to-evm", address, "1"],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute command: {e}")

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
