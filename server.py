import socket
import sys
import threading

commands = ["translate", "get", "put", "quit", "delete", "append"]


class ClientHandler(threading.Thread):
    """
    ClientHandler is a thread that handles communication with a single client.
    """

    def __init__(self, connection, address, server):
        """
        Initializes the ClientHandler thread with a connection, client address, and server reference.

        :param connection: The socket connection to the client.
        :param address: The client's IP address.
        :param server: Reference to the server instance.
        """
        super().__init__()
        self.connection = connection
        self.address = address
        self.server = server
        self.put_messages = []

    def run(self):
        """
        Main execution method of the thread.
        """
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
        """
        Handles the 'translate' command.
        """
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
        """
        Handles the 'put' command by storing messages sent from the client into the `put_messages` list.
        """
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
        """
        Handles the 'get' command by sending back stored messages to the client.
        """
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
        """
        Handles the 'delete' command by clearing the stored messages.
        """
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
        """
        Handles the 'append' command by adding new messages to the already stored messages.
        """
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
        """
        Handles the 'quit' command by closing the connection.
        """
        print(f"{self.address[0]} requested to quit. Closing connection.")
        self.connection.send("200 OK\nConnection closed.".encode())


class Server:
    """
    Server class that listens for client connections and spawns a new ClientHandler thread for each client.
    """

    def __init__(self, host, port):
        """
        Initializes the Server with the given host and port.

        :param host: Hostname or IP address to bind the server.
        :param port: Port number to bind the server.
        """
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        """
        Starts the server, binds the socket to the specified host and port, and listens for client connections.
        Spawns a new thread for each client connection.
        """
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
        """
        Stops the server and closes the server socket.
        """
        if self.server_socket:
            self.server_socket.close()


if __name__ == "__main__":
    host = socket.gethostname()
    port = 5991
    server = Server(host, port)

    try:
        server.start()
    except OSError as e:
        print(f"Error: {e}")
    finally:
        server.stop()
        print("Server stopped.")
