import socket

def printACK(msgReceived):
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

def clientProgram():
    message = ""
    host = "192.168.1.25"
    port = 32007
    
    #create a TCP based client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Note: no need for bind() call in client sockets...
        # just use the socket by calling connect()
        client.connect((host, port))

        while(True):
            message = input("What is your message? ")

            # if user inputs and exit cmd, client program will close
            if(message == "exit"):
                client.close()
                exit(0)
            elif(message == "kill"):                
                # Send a message
                client.send(message.encode())
                # Get the reply
                msgReceived = client.recv(1024)

                printACK(msgReceived)

                exit(0)
            else:
                try:
                    with open(message, "rb") as fi:
                        client.send(message.encode())
                        while True:
                            data = fi.read(1024) #read the file in chunks of 1024 bytes

                            if not data:
                                client.send("EOF".encode())
                                msgReceived = client.recv(1024)
                                printACK(msgReceived)
                                break
                            
                            client.send(data)
                            msgReceived = client.recv(1024)
                            printACK(msgReceived)
                except IOError:
                    print("You entered an invalid filename\n")
                    print("Please enter a valid name. Eg 'filename.txt'")
    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Could not connect to the server: {e}")

#Used to execute some code only if the file was run directly and not imported
if __name__ == '__main__':
    clientProgram()
