import socket

def clientProgram():
    message = ""

    #create a TCP based client socket
    echoClient = socket.socket()

    try:
        # Note: no need for bind() call in client sockets...
        # just use the socket by calling connect()
        echoClient.connect(("127.0.0.1", 32007))

        while(True):
            message = input("What is your message? ")

            # if user inputs and exit cmd, client program will close
            if(message == "exit"):
                echoClient.close()
                exit(0)

            # Send a message
            echoClient.send(message.encode())

            # Get the reply
            msgReceived = echoClient.recv(1024)

            # if the server did not return a message, exit client program
            # As the connection is likely lost
            if not msgReceived:
                print("Server did not recieve message, or ACK didn't return")
                print("Connection to the server has been lost. Restart of the")
                print("Client is required")
                exit(1)
            else:
                # Print the reply
                print("At client: %s"%msgReceived.decode())
    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Could not connect to the server: {e}")

#Used to execute some code only if the file was run directly and not imported
if __name__ == '__main__':
    clientProgram()
