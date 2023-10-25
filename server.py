import socket

def serverProgram():
    host = "192.168.1.25"
    port = 32007

    #A TCP based echo server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # This line allows the program to reuse the socket address
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        #Bind the IP address and the port number
        server.bind((host, port))

        #Listen for incoming connections
        server.listen()

        #Start accepting client connections
        while(True):
            (clientSocket, clientAdress) = server.accept()

            print("Connection from: " + str(clientAdress))

            filename = "output.txt"
            with open(filename, "wb") as fo:
                while True:
                    data = clientSocket.recv(1024)

                    #If client issues kill cmd, shutdown the server
                    if data.decode() == 'kill':
                        print("Kill cmd received. Shutting down the server")

                        #Send an ack back to the client and close the socket
                        clientSocket.send("ACKed, shutting Down Server".encode())
                        clientSocket.close()
                        server.close()

                        exit(0) #Exit with status code 0
                    elif data:
                        fo.write(data)
                        clientSocket.send("Data packet ACK".encode())
                    else:
                        # if data si not received break
                        break
    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Server could not be started: {e}")

#Used to execute some code only if the file was run directly and not imported
if __name__ == '__main__':
    serverProgram()
