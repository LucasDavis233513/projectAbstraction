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

        (clientSocket, clientAdress) = server.accept()

        print("Connection from: " + str(clientAdress))

        #Start accepting client connections
        while(True):
            filename = clientSocket.recv(1024).decode()
            data_buffer = []

            if filename == 'kill':
                clientSocket.send("ACKed, shutting Down Server".encode())

                print("Kill cmd received. Shutting down the server")

                clientSocket.close()
                server.close()
                exit(0) # Ext with status code 0

            while True:
                data = clientSocket.recv(1024)

                if data == b'EOF':
                    print("File recieved")

                    with open(filename, "wb") as fo:
                        for data in data_buffer:
                            fo.write(data)

                    del data_buffer
                
                    clientSocket.send("File recieved successfully. Data written to root dir.".encode())

                    break
                elif data:
                    data_buffer.append(data)    #Add received data to buffer
                    clientSocket.send("Data packet ACK".encode())
                else:
                    break

    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Server could not be started: {e}")

#Used to execute some code only if the file was run directly and not imported
if __name__ == '__main__':
    serverProgram()
