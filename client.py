import socket
import sys

commands = ["translate", "get", "put", "quit", "delete", "append"]


def runClient(portNum, hostName):
    try:
        clientSocket = socket.socket()
    except socket.error as err:
        print(f"Socket creation failed with error {err}")
        sys.exit()

    print("Trying to connect to host", hostName, "on port", portNum)
    clientSocket.connect((hostName, portNum))
    print("Connection successful")
    sWelcome = clientSocket.recv(1024).decode()
    print(sWelcome)
    return clientSocket


def validateText(prompt):
    text = input(prompt).strip()
    if not text:
        print("\n*****************************************************************")
        print("* Error: Empty input is not allowed. Please enter a valid text. *")
        print("*****************************************************************")
        return
    return text


def handle_translate(clientSocket):
    clientSocket.send("TRANSLATE".encode())
    sStatus = clientSocket.recv(1024).decode().strip()
    if sStatus == "200 OK":
        print("server: 200 OK")
        while True:
            text = validateText("client: ")
            if not text:
                continue
            clientSocket.send(text.encode())
            if text == ".":
                break

        while True:
            data = clientSocket.recv(1024).decode().strip()
            if not data:
                break
            if data != "completed":
                print(f"server: {data}")
                clientSocket.send("received".encode())
            else:
                print("==== Task has been accomplied ====")
                break


def handle_put(clientSocket):
    clientSocket.send("PUT".encode())
    sStatus = clientSocket.recv(1024).decode().strip()
    if sStatus == "200 OK":
        print("server: 200 OK")
        while True:
            text = validateText("client: ")
            if not text:
                continue
            clientSocket.send(text.encode())
            if text == ".":
                break
            confirmation = clientSocket.recv(1024).decode()
            if confirmation != "received":
                print("\n***********************************************************")
                print("* Error: Client did not confirm reception of the message. *")
                print("***********************************************************")
        response = clientSocket.recv(1024).decode().strip()
        if response == "completed":
            print("server: messages have been stored.")
            print("==== Task has been accomplied ====")
        else:
            print("server: Error, expected 'completed'.")


def handle_get(clientSocket):
    clientSocket.send("GET".encode())
    sStatus = clientSocket.recv(1024).decode()
    if sStatus == "200 OK":
        print("server: 200 OK")
        clientSocket.send("START".encode())
        while True:
            data = clientSocket.recv(1024).decode().strip()
            if not data:
                break
            if data != "completed":
                print(f"server: {data}")
                clientSocket.send("received".encode())
            else:
                print("==== Task has been accomplied ====")
                break

    else:
        print("\n***************************************")
        print(f"* ERROR: {sStatus} *")
        print("***************************************")


def handle_delete(clientSocket):
    clientSocket.send("DELETE".encode())
    sStatus = clientSocket.recv(1024).decode()
    if sStatus == "200 OK":
        print("server: 200 OK")
        clientSocket.send("START".encode())
        while True:
            data = clientSocket.recv(1024).decode().strip()
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


def handle_append(clientSocket):
    clientSocket.send("APPEND".encode())
    sStatus = clientSocket.recv(1024).decode().strip()
    if sStatus == "200 OK":
        print("server: 200 OK")
        while True:
            text = validateText("client: ")
            if not text:
                continue
            clientSocket.send(text.encode())
            if text == ".":
                break
            confirmation = clientSocket.recv(1024).decode()
            if confirmation != "received":
                print("\n***********************************************************")
                print("* Error: Client did not confirm reception of the message. *")
                print("***********************************************************")
        response = clientSocket.recv(1024).decode().strip()
        if response == "completed":
            print("server: messages have been stored.")
            print("==== Task has been accomplied ====")
        else:
            print("server: Error, expected 'completed'.")


def mainFunction(clientSocket):
    while True:
        print("\n================================================")
        print("Available commands: TRANSLATE / PUT / GET / DELETE/ APPEND/ QUIT")
        command = input("Enter command: ").strip().lower()
        if not command:
            print("\n*****************************************************************")
            print("* Error: Command cannot be empty. Please enter a valid command. *")
            print("*****************************************************************")
            continue

        if command == "translate":
            handle_translate(clientSocket)
        elif command == "put":
            handle_put(clientSocket)
        elif command == "get":
            handle_get(clientSocket)
        elif command == "delete":
            print("# DELETE command to clear the stored messages in the server. #")
            handle_delete(clientSocket)
        elif command == "append":
            print(
                "# APPEND command to append/ store additional text to the previously stored messages in the server #"
            )
            handle_append(clientSocket)
        elif command == "quit":
            clientSocket.send("QUIT".encode())
            print("Closing connection.")
            clientSocket.close()
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
    portNum = 5991
    hostName = socket.gethostname()
    clientSocket = runClient(portNum, hostName)
    mainFunction(clientSocket)
