import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


# Function to run startup commands
def run_startup_commands():
    commands = [
        'python3 stop_xApp.py'  # Ensure stop_xApp.py is executed to handle any cleanup
    ]

    for command in commands:
        print(f"Running command: {command}")
        log_file = command.split()[1].replace('.py', '.log')  # Create log file based on the script name
        with open(log_file, 'w') as log:
            subprocess.Popen(command, shell=True, stdout=log, stderr=log, executable='/bin/bash')


# Define the request handler
class BashRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8').strip()

        print(f"Received POST data: {post_data}")

        try:
            if post_data == "start":
                # Log file for the process
                log_file = 'xapp_rc_handover_ctrl.log'  # Fixed log file name for the process
                with open(log_file, 'w') as log:
                    print(
                        f"Starting process: ./build/examples/xApp/c/ctrl/xapp_rc_handover_ctrl, logging to: {log_file}")
                    process = subprocess.Popen(
                        "stdbuf -oL -eL ./build/examples/xApp/c/ctrl/xapp_rc_handover_ctrl",
                        shell=True, stdout=log, stderr=log, executable='/bin/bash'
                    )
                    print(f"Process started with PID: {process.pid}")

                # Add CORS headers here
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
                self.end_headers()
                self.wfile.write(b"xApp process started.")

            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Invalid command. Use 'start'.")

        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
            self.end_headers()
            self.wfile.write(f"Error processing request: {e}".encode('utf-8'))

    def do_GET(self):
        print("Received GET request.")
        self.send_response(405)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Use POST to start the xApp process.")


def run(server_class=HTTPServer, handler_class=BashRequestHandler, port=38868):
    run_startup_commands()

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
