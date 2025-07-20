import socket

def start_server(ip, route_handler):
    print("📡 Starting server setup...")

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("✅ Socket created")

        addr = socket.getaddrinfo(ip, 80)[0][-1]
        server_socket.bind(addr)
        print(f"✅ Bound to {ip}:80")

        server_socket.listen(1)
        print("✅ Listening for connections...")

        while True:
            print("⏳ Waiting for client...")
            try:
                client_socket, client_addr = server_socket.accept()
                print("🌐 Client connected from", client_addr)

                request = client_socket.recv(1024)
                print("📩 Raw request:", request)

                try:
                    line = request.decode().split("\r\n")[0]
                    method, path, _ = line.split(" ")
                    print(f"➡️  Method: {method}, Path: {path}")
                    response = route_handler(path)
                except Exception as parse_error:
                    print("❌ Request parse error:", parse_error)
                    response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid request"

                client_socket.send(response.encode())
                client_socket.close()
                print("✅ Response sent\n")

            except Exception as conn_error:
                print("❌ Connection error:", conn_error)

    except Exception as startup_error:
        print("❌ Server startup error:", startup_error)

    finally:
        print("🧹 Closing server socket...")
        try:
            server_socket.close()
        except:
            print("⚠️ Could not close server socket")

