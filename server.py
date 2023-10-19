import socket

def serverProgram():
    #A TCP based echo server
    echoServer = socket.socket()

    # This line allows the program to reuse the socket address
    echoServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        #Bind the IP address and the port number
        echoServer.bind(("127.0.0.1", 32007))

        #Listen for incoming connections
        echoServer.listen()

        #Start accepting client connections
        while(True):
            (clientSocket, clientAdress) = echoServer.accept()

            print("Connection from: " + str(clientAdress))
            while(True):
                data = clientSocket.recv(1024)
                print("At server: %s"%data)

                #If client issues kill cmd, shutdown the server
                if(data.decode() == 'kill'):
                    print("Kill cmd recieved. Shutting down the server")

                    #Send an ack back to the client and close the socket
                    clientSocket.send("ACKed, shutting Down Server".encode())
                    clientSocket.close()
                    echoServer.close()

                    exit(0) #Exit with status code 0
                elif(data != b''):
                    #send back what you recevied
                    clientSocket.send(data+(" ACKed by server".encode()))
                elif not data:
                    # if data si not received break
                    break
    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Server could not be started: {e}")

#Used to execute some code only if the file was run directly and not imported
if __name__ == '__main__':
    serverProgram()
