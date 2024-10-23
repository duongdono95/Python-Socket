import socket
import sys


class TCPClient:
    """
    A TCP Client class that manages the connection to the server and processes user commands.
    """

    def __init__(self, portNum, hostName):
        """
        Initializes the client by establishing a connection to the server.
        :param portNum: The port number on which to connect to the server.
        :param hostName: The hostname or IP address of the server.
        """
        self.clientSocket = self.runClient(portNum, hostName)

    def runClient(self, portNum, hostName):
        """
        Establishes a connection to the server.
        :param portNum: The port number on which to connect to the server.
        :param hostName: The hostname or IP address of the server.
        :return: The socket object representing the client-server connection.
        """
        try:
            clientSocket = socket.socket()
        except socket.error as err:
            print(f"Socket creation failed with error {err}")
            sys.exit()

        print(f"Trying to connect to host {hostName} on port {portNum}")
        clientSocket.connect((hostName, portNum))
        print("Connection successful")
        sWelcome = clientSocket.recv(1024).decode()
        print(sWelcome)
        return clientSocket

    def validateText(self, prompt):
        """
        Prompts the user for input, ensuring that the input is non-empty.
        :param prompt: The prompt text for user input.
        :return: The valid input string or None if input is invalid.
        """
        text = input(prompt).strip()
        if not text:
            print("\n*****************************************************************")
            print("* Error: Empty input is not allowed. Please enter a valid text. *")
            print("*****************************************************************")
            return None
        return text

    def handle_translate(self):
        """
        Handles the 'TRANSLATE' command, sending text to the server for translation to uppercase.
        """
        self.clientSocket.send("TRANSLATE".encode())
        sStatus = self.clientSocket.recv(1024).decode().strip()
        if sStatus == "200 OK":
            print("server: 200 OK")
            while True:
                text = self.validateText("client: ")
                if not text:
                    continue
                self.clientSocket.send(text.encode())
                if text == ".":
                    break

            while True:
                data = self.clientSocket.recv(1024).decode().strip()
                if not data:
                    break
                if data != "completed":
                    print(f"server: {data}")
                    self.clientSocket.send("received".encode())
                else:
                    print("==== Task has been accomplied ====")
                    break

    def handle_put(self):
        """
        Handles the 'PUT' command, allowing the user to store text on the server.
        """
        self.clientSocket.send("PUT".encode())
        sStatus = self.clientSocket.recv(1024).decode().strip()
        if sStatus == "200 OK":
            print("server: 200 OK")
            while True:
                text = self.validateText("client: ")
                if not text:
                    continue
                self.clientSocket.send(text.encode())
                if text == ".":
                    break
                confirmation = self.clientSocket.recv(1024).decode()
                if confirmation != "received":
                    print(
                        "\n***********************************************************"
                    )
                    print("* Error: Client did not confirm reception of the message. *")
                    print("***********************************************************")
            response = self.clientSocket.recv(1024).decode().strip()
            if response == "completed":
                print("server: messages have been stored.")
                print("==== Task has been accomplied ====")
            else:
                print("server: Error, expected 'completed'.")

    def handle_get(self):
        """
        Handles the 'GET' command, retrieving and displaying stored messages from the server.
        """
        self.clientSocket.send("GET".encode())
        sStatus = self.clientSocket.recv(1024).decode()
        if sStatus == "200 OK":
            print("server: 200 OK")
            self.clientSocket.send("START".encode())
            while True:
                data = self.clientSocket.recv(1024).decode().strip()
                if not data:
                    break
                if data != "completed":
                    print(f"server: {data}")
                    self.clientSocket.send("received".encode())
                else:
                    print("==== Task has been accomplied ====")
                    break
        else:
            print("\n***************************************")
            print(f"* ERROR: {sStatus} *")
            print("***************************************")

    def handle_delete(self):
        """
        Handles the 'DELETE' command, clearing stored messages from the server.
        """
        self.clientSocket.send("DELETE".encode())
        sStatus = self.clientSocket.recv(1024).decode()
        if sStatus == "200 OK":
            print("server: 200 OK")
            self.clientSocket.send("START".encode())
            while True:
                data = self.clientSocket.recv(1024).decode().strip()
                if not data:
                    break
                if data == "completed":
                    print("==== Task has been accomplied ====")
                    break
                else:
                    print("\n***************************************")
                    print(f"* ERROR: Unexpected Error from Delete command *")
                    print("***************************************")
        else:
            print("\n***************************************")
            print(f"* ERROR: {sStatus} *")
            print("***************************************")

    def handle_append(self):
        """
        Handles the 'APPEND' command, adding more text to the already stored messages on the server.
        """
        self.clientSocket.send("APPEND".encode())
        sStatus = self.clientSocket.recv(1024).decode().strip()
        if sStatus == "200 OK":
            print("server: 200 OK")
            while True:
                text = self.validateText("client: ")
                if not text:
                    continue
                self.clientSocket.send(text.encode())
                if text == ".":
                    break
                confirmation = self.clientSocket.recv(1024).decode()
                if confirmation != "received":
                    print(
                        "\n***********************************************************"
                    )
                    print("* Error: Client did not confirm reception of the message. *")
                    print("***********************************************************")
            response = self.clientSocket.recv(1024).decode().strip()
            if response == "completed":
                print("server: messages have been stored.")
                print("==== Task has been accomplied ====")
            else:
                print("server: Error, expected 'completed'.")

    def mainFunction(self):
        """
        Main function that prompts the user for commands and directs them to the appropriate handler.
        """
        while True:
            print("\n================================================")
            print("Available commands: TRANSLATE / PUT / GET / DELETE/ APPEND/ QUIT")
            command = input("Enter command: ").strip().lower()
            if not command:
                print(
                    "\n*****************************************************************"
                )
                print(
                    "* Error: Command cannot be empty. Please enter a valid command. *"
                )
                print(
                    "*****************************************************************"
                )
                continue

            if command == "translate":
                self.handle_translate()
            elif command == "put":
                self.handle_put()
            elif command == "get":
                self.handle_get()
            elif command == "delete":
                print("# DELETE command to clear the stored messages in the server. #")
                self.handle_delete()
            elif command == "append":
                print(
                    "# APPEND command to append/ store additional text to the previously stored messages in the server #"
                )
                self.handle_append()
            elif command == "quit":
                self.clientSocket.send("QUIT".encode())
                print("Closing connection.")
                self.clientSocket.close()
                break
            else:
                print(
                    "\n********************************************************************************************************"
                )
                print(
                    "* Error: Invalid command. Please use one of the following: TRANSLATE / PUT / GET / DELETE/ APPEND/ QUIT. *"
                )
                print(
                    "********************************************************************************************************"
                )


if __name__ == "__main__":
    """
    Entry point of the client application. Connects to the server and starts the main command loop.
    """
    portNum = 5991
    hostName = socket.gethostname()
    client = TCPClient(
        portNum, hostName
    )  # Create a TCPClient instance and connect to the server
    client.mainFunction()  # Start the main command loop
