import socket
from handlers import route_handler

def start_server(ip, route_handler):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Add this line to allow socket reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_address = socket.getaddrinfo(ip, 80)[0][-1]
    
    try:
        server_socket.bind(server_address)
        server_socket.listen(1)
        print(f"Web server running on http://{ip}:80")
        
        while True:
            client_socket, client_addr = server_socket.accept()
            print("\n--- New Connection ---")
            print("Client connected from", client_addr)
            try:
                request = client_socket.recv(1024).decode('utf-8')
                print("Raw request:", request)
                
                request_lines = request.split('\r\n')
                print("Request lines:", request_lines)
                
                if request_lines:
                    first_line = request_lines[0]
                    print("First line:", first_line)
                    parts = first_line.split(' ')
                    print("Parts:", parts)
                    
                    if len(parts) >= 2:
                        path = parts[1]
                        print("Extracted path:", path)
                        response = route_handler(path)
                    else:
                        print("Invalid request format - not enough parts")
                        response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid request format"
                else:
                    print("Empty request lines")
                    response = "HTTP/1.1 400 Bad Request\r\n\r\nEmpty request"
                    
                client_socket.send(response.encode('utf-8'))
            except Exception as error:
                print("Error handling request:", error)
                response = "HTTP/1.1 500 Internal Server Error\r\n\r\nServer error"
                client_socket.send(response.encode('utf-8'))
            finally:
                client_socket.close()
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

def start_server_thread(ip, route_handler):
    try:
        _thread.start_new_thread(start_server, (ip, route_handler))
    except Exception as e:
        print(f"Error starting server thread: {e}")

