import socket
import sys

commands = ["translate", "get", "put", "quit"]


def OpenSocket(port):
    # retrieve the host name
    hostName = socket.gethostname()
    print("host name", hostName)
    theSocket = socket.socket()
    # Allow the socket to reuse the address/port even if it's in TIME_WAIT state
    theSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the port
    theSocket.bind((hostName, port))

    print(f"Listening for a connection on port {port}")
    # listen sets the number of clients the server can listen to at one time
    theSocket.listen()

    # accept a new connection
    connection, address = theSocket.accept()

    print("Connected!")
    return theSocket, connection, address


def runServer(portNum):
    print("====================================================")
    serverSocket, connection, address = OpenSocket(portNum)
    print("Connection from: " + str(address))
    print("Sending Welcome Message")
    connection.send("Welcome to Dono Server".encode())
    print("====================================================")
    return serverSocket, connection, address


def validateCommand(cMessage):
    command = ""
    error = None
    if cMessage in commands:
        command = cMessage
    else:
        print("Error: 400 - Invalid Input")
        error = "Error: 400 - The input must be TRANSLATE or GET or PUT or QUIT"

    return command, error


def translateFunction(connection):
    messageArr = []
    translatedMessageArr = []
    while True:
        message = connection.recv(1024).decode()
        print("message", message)
        if message != "done":
            print("Received message:", message)
            messageArr.append(message)
            translatedMessageArr.append(message.upper())
            connection.send("next".encode())
        else:
            print("Messages received:", messageArr)
            print("Translation complete:", translatedMessageArr)
            for item in translatedMessageArr:
                connection.send(item.encode())
                cMessage = connection.recv(1024).decode()
                print("client received item", cMessage)
            connection.send("done".encode())
            break


def putFunction(
    connection,
):
    messageArr = []
    while True:
        message = connection.recv(1024).decode()
        if message != "done":
            messageArr.append(message)
            connection.send("next".encode())
        else:
            print("All message received:", messageArr)
            break
    return messageArr


def getFunction(connection, putMessageArr):
    if len(putMessageArr) == 0:
        print("**** No Messages were saved ****")
        connection.send("GET-ERROR".encode())
    else:
        while True:
            if len(putMessageArr) == 0:
                print("**** No Messages were saved ****")
                connection.send("GET-ERROR".encode())
                break
            else:
                print("execute")
                while True:
                    for item in putMessageArr:
                        print("item", item)
                        connection.send(item.encode())
                        cResponse = connection.recv(1024).decode()
                        if cResponse == "next":
                            print("**** Server acknowledged the message ****")
                    connection.send("done".encode())
                    break
            break


def mainFunction(serverSocket, connection, address):
    putMessageArr = []
    while True:
        try:
            inputCommand = connection.recv(1024).decode().lower()
            print("Requested Command: ", inputCommand.upper())
            command = None
            validatedCommand, error = validateCommand(inputCommand)
            command = validatedCommand

            if error:
                connection.send(error.encode())
            else:
                connection.send("200 OK".encode())
                client_ack = connection.recv(1024).decode()
                if client_ack != "ACK":
                    print("Did not receive acknowledgment from the client.")
                    continue

            if command == "quit":
                print("Client requested to quit, closing connection.")
                connection.close()
                break

            if command == "translate":
                translateFunction(connection)

            if command == "put":
                messages = putFunction(connection)
                putMessageArr = messages

            if command == "get":
                getFunction(connection, putMessageArr)

        except ConnectionResetError:
            print("Client disconnected unexpectedly (ConnectionResetError).")
            break


if __name__ == "__main__":
    portNum = 5991
    serverSocket, connection, address = runServer(portNum)
    mainFunction(serverSocket, connection, address)
