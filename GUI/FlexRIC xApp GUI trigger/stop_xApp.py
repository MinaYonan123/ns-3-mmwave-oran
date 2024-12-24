import os
import signal
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

class BashRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Process name to stop
        process_name = "xapp_rc_handove"

        print(f"Received request to stop process: {process_name}")

        # Stop the process with the specified name
        try:
            # Get the process ID(s) for the process with the name or partial name
            result = subprocess.run(f"pgrep -f {process_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            pids = result.stdout.strip().split('\n')

            if pids and pids[0]:
                # Kill the processes
                for pid in pids:
                    print(f"Stopping process with PID: {pid}")
                    try:
                        os.kill(int(pid), signal.SIGTERM)  # Send SIGTERM to the process
                        # Reap zombie processes if possible
                        os.waitpid(int(pid), 0)
                        print(f"Process with PID {pid} successfully reaped.")
                    except (ProcessLookupError, ChildProcessError):
                        print(f"Process with PID {pid} is defunct or already reaped.")
                        continue

                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*') # Allow requests from any origin
                self.end_headers()
                self.wfile.write(f"Process(es) with name '{process_name}' terminated and reaped.".encode('utf-8'))
            else:
                print("No processes found to stop.")
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*') # Allow requests from any origin
                self.end_headers()
                self.wfile.write(f"No process found with name '{process_name}'.".encode('utf-8'))

        except Exception as e:
            print(f"Error stopping process: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow requests from any origin
            self.end_headers()
            self.wfile.write(f"Error stopping process: {e}".encode('utf-8'))

    def do_GET(self):
        self.send_response(405)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Use POST to stop processes by partial name.")

def run(server_class=HTTPServer, handler_class=BashRequestHandler, port=38869):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
