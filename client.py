import socket

def printACK(msgReceived):
    # if the server did not return a file, exit client program
    # As the connection is likely lost
    if not msgReceived:
        print("Server did not recieve file, or ACK didn't return")
        print("Connection to the server has been lost. Restart of the")
        print("Client is required")
        exit(1)
    else:
        # Print the reply
        print("At client: %s"%msgReceived.decode())

def clientProgram():
    file = ""
    host = "192.168.1.25"
    port = 32007
    
    #create a TCP based client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to the server
        client.connect((host, port))

        while(True):
            file = input("What is the files name: ")

            # if user inputs and exit cmd, client program will close
            if(file == "exit"):
                client.close()
                exit(0)
            elif(file == "kill"): # if user inputs a kill cmd, client and server program will close            
                client.send(file.encode())          # send the kill cmd
                msgReceived = client.recv(1024)     # wait for ACK
                printACK(msgReceived)               # print the ACK

                exit(0)
            else:
                try:
                    #Attempt to open file with read bytes option.
                    with open(file, "rb") as fi:
                        client.send(file.encode()) # Send the filename to the server
                        while True:
                            data = fi.read(1024) #read the file in chunks of 1024 bytes
                            
                            # If data is NULL (all bytes are read) break from the while loop
                            if not data:        
                                client.send("EOF".encode())         # send an EOF message
                                msgReceived = client.recv(1024)     # wait for final ACK message
                                printACK(msgReceived)               # print ACK
                                break
                            
                            client.send(data)                   # Send the data to the server
                            msgReceived = client.recv(1024)     # Wait for ACK message
                            printACK(msgReceived)               # Print ACK
                except IOError:     # if an error was encountered when reading from the file, we will error out
                    print("You entered an invalid filename\n")
                    print("Please enter a valid name. Eg 'filename.txt'")
    except socket.error as e:
        # Return error file if and error occured creating or using the socket
        print(f"Could not connect to the server: {e}")

#Used to execute some code only if the file was run directly and not imported
if __name__ == '__main__':
    clientProgram()
