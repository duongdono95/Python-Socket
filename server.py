import socket
import sys
import threading

commands = ["translate", "get", "put", "quit", "delete", "append"]


class ClientHandler(threading.Thread):
    def __init__(self, connection, address, server):
        super().__init__()
        self.connection = connection
        self.address = address
        self.server = server
        self.put_messages = []

    def run(self):
        print(f"server: got connection from client {self.address[0]}")
        self.connection.send("Server is ready...\n".encode())

        while True:
            try:
                command = self.connection.recv(1024).decode().strip()
                if not command:
                    break
                if command.lower() == "translate":
                    self.handle_translate()
                elif command.lower() == "put":
                    self.handle_put()
                elif command.lower() == "get":
                    self.handle_get()
                elif command.lower() == "append":
                    self.handle_append()
                elif command.lower() == "delete":
                    self.handle_delete()
                elif command.lower() == "quit":
                    self.handle_quit()
                    break
                else:
                    self.connection.send("400 Command not valid.\n".encode())
            except ConnectionResetError:
                print(
                    f"Client {self.address[0]} disconnected unexpectedly (ConnectionResetError)."
                )
                break
        self.connection.close()
        print(f"Connection with client {self.address[0]} closed.")

    def handle_translate(self):
        self.connection.send("200 OK".encode())
        lines = []
        while True:
            data = self.connection.recv(1024).decode().strip()
            if data == ".":
                break
            lines.append(data.upper())

        for line in lines:
            self.connection.send((line + "\n").encode())
            confirmation = self.connection.recv(1024).decode().strip()
            if confirmation != "received":
                print(
                    f"Error: {self.address[0]} did not confirm reception of the line."
                )
                break

        self.connection.send("completed".encode())
        print(f"{self.address[0]}: Translate command handled.")

    def handle_put(self):
        self.connection.send("200 OK\n".encode())
        received_lines = []
        while True:
            data = self.connection.recv(1024).decode().strip()
            if data == ".":
                break
            if data:
                received_lines.append(data)
                self.connection.send("received".encode())

        self.put_messages = received_lines
        self.connection.send("completed\n".encode())
        print(f"{self.address[0]}: Put command handled.")

    def handle_get(self):
        if not self.put_messages:
            self.connection.send("No messages stored in the server.".encode())
        else:
            self.connection.send("200 OK".encode())
            start = self.connection.recv(1024).decode()
            if start == "START":
                for item in self.put_messages:
                    self.connection.send(item.encode())
                    confirmation = self.connection.recv(1024).decode()
                    if confirmation != "received":
                        print(
                            f"Error: {self.address[0]} did not confirm reception of the message."
                        )
            self.connection.send("completed".encode())
            print(f"{self.address[0]}: Get command handled.")

    def handle_delete(self):
        if not self.put_messages:
            self.connection.send("No messages stored in the server.".encode())
        else:
            self.connection.send("200 OK".encode())
            start = self.connection.recv(1024).decode()
            if start == "START":
                self.put_messages.clear()
            self.connection.send("completed".encode())
            print(f"{self.address[0]}: Delete command handled.")

    def handle_append(self):
        self.connection.send("200 OK\n".encode())
        while True:
            data = self.connection.recv(1024).decode().strip()
            if data == ".":
                break
            if data:
                self.put_messages.append(data)
                self.connection.send("received".encode())
        self.connection.send("completed\n".encode())
        print(f"{self.address[0]}: Append command handled.")

    def handle_quit(self):
        print(f"{self.address[0]} requested to quit. Closing connection.")
        self.connection.send("200 OK\nConnection closed.".encode())


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("\n===============================================")
        print(f"Server started on {self.host}:{self.port}")
        print("Waiting for connections...")
        print("===============================================\n")
        while True:
            connection, address = self.server_socket.accept()
            # Start a new thread for each client
            client_handler = ClientHandler(connection, address, self)
            client_handler.start()

    def stop(self):
        if self.server_socket:
            self.server_socket.close()


if __name__ == "__main__":
    host = socket.gethostname()  # Use the actual host machine's IP for external clients
    port = 5991
    server = Server(host, port)

    try:
        server.start()
    except OSError as e:
        print(f"Error: {e}")
    finally:
        server.stop()
        print("Server stopped.")
