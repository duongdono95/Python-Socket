import socket
import sys

commands = ["translate", "get", "put", "quit"]


def runClient(portNum, hostName):
    # create a socket object
    try:
        clientSocket = socket.socket()
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    if clientSocket:
        print("Trying to connect to host", hostName, "on port", portNum)
        clientSocket.connect((hostName, portNum))
        # close the connection
        print("Connection successful, closing connection")
        print("Waiting for the server welcome message")
        sWelcome = clientSocket.recv(1024).decode()
        # recv to receive data from the server + decode to conver UTF-8 string to python string
        print(sWelcome)
        return clientSocket


def getValidInput(prompt):
    while True:
        userInput = input(prompt)
        if len(userInput.strip()) == 0:
            print("Input cannot be empty, please try again.")
        else:
            return userInput


def translateFunction(clientSocket):
    messageArr = []
    print(
        "Please provide message to translate (end action by entering '.' in a new line)"
    )
    # ------------------------- take user's input & send to server -------------------- #
    while True:
        message = getValidInput("Your message: ")
        if message != ".":
            messageArr.append(message)
        else:
            for item in messageArr:
                clientSocket.send(item.encode())
                sResponse = clientSocket.recv(1024).decode()
                if sResponse == "next":
                    print("**** Server acknowledged the message ****")
            clientSocket.send("done".encode())
            print("**** All messages sent ****")
            break
    # ------------------------- get translated messages -------------------- #

    while True:
        translatedMessageArr = []
        translatedMessage = clientSocket.recv(1024).decode()
        if translatedMessage != "done":
            print("Server:", translatedMessage)
            translatedMessageArr.append(translatedMessage)
            clientSocket.send("next".encode())
        else:
            print("all translated messages:", translatedMessageArr)
            break
    return translatedMessageArr


def putFunction(clientSocket):
    print("Please provide message to put (end action by entering '.' in a new line)")
    messages = []
    while True:
        inputMessage = getValidInput("Your Message: ")
        if inputMessage != ".":
            messages.append(inputMessage)
        else:
            for item in messages:
                clientSocket.send(item.encode())
                sResponse = clientSocket.recv(1024).decode()
                if sResponse == "next":
                    print("**** Server acknowledged the message ****")
            clientSocket.send("done".encode())
            print("**** All Messages have been sent ****")
            break


def getFunction(clientSocket):
    messages = []
    sResponse = clientSocket.recv(1024).decode()
    if sResponse == "GET-ERROR":
        print(
            "**** Server: No Messages were saved, please execute PUT command first. ****"
        )
    else:
        print("execute")
        clientSocket.send("start".encode())
        message = clientSocket.recv(1024).decode()
        print("execute 2", message)
        if message != "done":
            print("execute 3")
            print("Sever: ", message)
            messages.append(message)
            clientSocket.send("next".encode())
        else:
            print("All message received: ", messages)
    return messages


def mainFunction(clientSocket):
    try:
        while True:
            inputCommand = getValidInput(
                "Please enter your choice of command (translate/ get/ put/ quit): "
            )
            clientSocket.send(inputCommand.encode().lower())

            sResponse = clientSocket.recv(1024).decode()
            print("***** SERVER:", sResponse)
            clientSocket.send("ACK".encode())
            if sResponse == "200 OK" and inputCommand.lower() in commands:
                if inputCommand == "quit":
                    print("Closing Connection.")
                    clientSocket.close()
                    break
                if inputCommand == "translate":
                    print("==================================================")
                    translatedMessageArr = translateFunction(clientSocket)
                    print("==================================================")
                if inputCommand == "put":
                    print("==================================================")
                    putFunction(clientSocket)
                    print("==================================================")
                if inputCommand == "get":
                    print("==================================================")
                    getFunction(clientSocket)
                    print("==================================================")

    except socket.error as err:
        print("socket connection failed with error %s" % (err))


if __name__ == "__main__":
    portNum = 5991
    hostName = socket.gethostname()
    clientSocket = runClient(portNum, hostName)
    mainFunction(clientSocket)
