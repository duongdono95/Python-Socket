import socket
import sys
import threading

commands = ["translate", "get", "put", "quit", "delete", "append"]


def handle_quit(address, serverSocket, connection):
    print(f"{address[0]} requested to quit. Closing connection.")
    connection.close()
    serverSocket.close()
    sys.exit(0)  # Exit the server


def handle_translate(address, connection):
    connection.send("200 OK".encode())
    lines = []
    while True:
        data = connection.recv(1024).decode().strip()
        if not data:
            continue
        if data == ".":
            print(f"{address[0]}: Received all messages for translating.")
            break
        lines.append(data.upper())

    for line in lines:
        connection.send((line + "\n").encode())
        confirmation = connection.recv(1024).decode().strip()
        if confirmation != "received":
            print(f"Error: {address[0]} did not confirm reception of the line.")
            break

    connection.send("completed".encode())
    print(f"{address[0]}: Translate command handled.")


def handle_put(address, connection):
    connection.send("200 OK\n".encode())
    received_lines = []

    while True:
        data = connection.recv(1024).decode().strip()
        if data == ".":
            break
        if data:
            received_lines.append(data)
            connection.send("received".encode())
    connection.send("completed\n".encode())
    print(f"{address[0]}: Put command handled.")
    return received_lines


def handle_get(address, connection, put_messages):
    print("put messages:", put_messages)
    if not put_messages:
        connection.send("No messages stored in the server.".encode())
    else:
        connection.send("200 OK".encode())
        start = connection.recv(1024).decode()
        if start == "START":
            for item in put_messages:
                connection.send(item.encode())
                confirmation = connection.recv(1024).decode()
                print("get confirmation: ", confirmation)
                if confirmation != "received":
                    print(
                        f"Error: {address[0]} did not confirm reception of the message. "
                    )
        connection.send("completed".encode())
        print(f"{address[0]}: Get command handled")


def handle_delete(address, connection, put_messages):
    print("put messages:", put_messages)
    if not put_messages:
        connection.send("No messages stored in the server.".encode())
    else:
        connection.send("200 OK".encode())
        start = connection.recv(1024).decode()
        if start == "START":
            put_messages = []
        connection.send("completed".encode())
        print(f"{address[0]}: Delete command handled")
        return put_messages


def handle_append(address, connection, put_messages):
    connection.send("200 OK\n".encode())
    while True:
        data = connection.recv(1024).decode().strip()
        if data == ".":
            break
        if data:
            put_messages.append(data)
            connection.send("received".encode())
    connection.send("completed\n".encode())
    print(f"{address[0]}: Append command handled")
    return put_messages


def client_thread(connection, address):
    print(f"server: got connection from client {address[0]}")
    connection.send("Server is ready...\n".encode())
    put_messages = []
    while True:
        try:
            command = connection.recv(1024).decode().strip()
            if not command:
                break
            if command.lower() == "translate":
                print(f"{address[0]} sends TRANSLATE")
                handle_translate(address, connection)
            elif command.lower() == "put":
                print(f"{address[0]} sends PUT")
                stored_messages = handle_put(address, connection)
                put_messages = stored_messages
            elif command.lower() == "get":
                print(f"{address[0]} sends GET")
                handle_get(address, connection, put_messages)

            elif command.lower() == "append":
                print(f"{address[0]} sends APPEND")
                updated_messages = handle_append(address, connection, put_messages)
                put_messages = updated_messages
            elif command.lower() == "delete":
                print(f"{address[0]} sends delete")
                cleared_put_message = handle_delete(address, connection, put_messages)
                put_messages = cleared_put_message
            else:
                connection.send("400 Command not valid.\n".encode())
        except ConnectionResetError:
            print("Client disconnected unexpectedly (ConnectionResetError).")
            break
    connection.close()
    print(f"Connection with client {address[0]} closed.")


def OpenSocket(port):
    hostName = socket.gethostname()
    print("host name", hostName)
    theSocket = socket.socket()
    theSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    theSocket.bind((hostName, port))
    print(f"Listening for a connection on port {port}")
    theSocket.listen()
    return theSocket


if __name__ == "__main__":
    portNum = 5991
    try:
        serverSocket = OpenSocket(portNum)
        print("\n================================================")
        print("Server is running and waiting for connections...")
        print("================================================\n")

        while True:
            connection, address = serverSocket.accept()
            threading.Thread(target=client_thread, args=(connection, address)).start()
    except OSError as e:
        print(f"Error: {e}")
    finally:
        serverSocket.close()
        print("Server socket closed.")
