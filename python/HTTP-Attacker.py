import argparse
import os
import socketserver
import http.server
import base64
import logging
import sys
# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Check if the custom header "X-Base64-Data" is present in the request
        if "X-Base64-Data" in self.headers:
            base64_data = self.headers["X-Base64-Data"];
            f_name = self.headers["X-FName"];
            print(f_name)
            try:
                decoded_data = base64.b64decode(base64_data)
                
                # Save the decoded data to a file in the output directory
                if self.server.output_dir:
                    with open(os.path.join(self.server.output_dir, f_name), "wb") as f:
                        f.write(decoded_data)
                
                # Respond with a success message
                response_message = "Decryption successful. Hello, world!"
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(response_message.encode("utf-8"))
            except Exception as e:
                # Log the error and respond with an error message
                logging.error(f"Error decoding base64 data: {str(e)}")
                response_message = "Error decoding base64 data."
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(response_message.encode("utf-8"))
        else:
            # If the custom header is not present, serve files as usual
            super().do_GET()

class CustomHTTPServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, output_dir=None):
        self.output_dir = output_dir
        super().__init__(server_address, RequestHandlerClass)

def main():
    parser = argparse.ArgumentParser(description="HTTP Server with Custom Options")

    parser.add_argument(
        "-l",
        "--listen-host",
        default="0.0.0.0",
        help="The address to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=80,
        help="The port to listen on (default: 80)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default=os.getcwd(),
        help="The output directory (default: working directory)",
    )

    args = parser.parse_args()

    listen_host = args.listen_host
    port = args.port
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        print(f"Error: The output directory '{output_dir}' does not exist.")
        sys.exit(1)

    #os.chdir(output_dir)
    output_dir= os.path.join(os.getcwd(),output_dir);

    try:
        server = CustomHTTPServer(
            (listen_host, port),
            CustomRequestHandler,
            output_dir=output_dir,
        )
        print(f"Server is listening on {listen_host}:{port}...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
            try:
                server.server_close()
            except:
                pass
if __name__ == "__main__":
    main()
