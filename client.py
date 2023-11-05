import socket
import time

WINDOW_SIZE = 10

def checkSum(_data):
    checksum = 0
    _data = [int.from_bytes(_data[i:i+2], 'little') for i in range(0, len(_data), 2)]

    for data16 in _data:
        checksum += data16

        # while there is a
        while ((checksum >> 16) > 0):
            # Add cary to the sum
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

    # Ones complement
    checksum = ~checksum & 0xFFFF

    return checksum

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

def sendFile(_file, _socket):
    try:
        #Attempt to open file with read bytes option.
        with open(_file, "rb") as fi:
            _socket.send(_file.encode())  # Send the filename to the server
            seq_num = 0                   # Initialize the sequence numer
            window_packet = []            # Create a window buffer to store the packets

            while True:
                data = fi.read(1024) #read the file in chunks of 1024 bytes
                
                # If data is NULL (all bytes are read) break from the while loop
                if not data:        
                    _socket.send("EOF".encode())              # send an EOF message
                    msgReceived = _socket.recv(1024)          # wait for final ACK message
                    printACK(msgReceived)                     # print ACK
                    break

                checksum = checkSum(data)
                # append the seq_num to the start and checksum to the end of the data bytes and save to a packet
                packet_to_send =  seq_num.to_bytes(2, 'little') + data + checksum.to_bytes(2, 'little')
                window_packet.append(packet_to_send)

                seq_num += 1                            # increment seq_num

                if len(window_packet) == WINDOW_SIZE:
                    for packet in window_packet:
                        _socket.send(packet)
                        time.sleep(0.01)

                    msgReceived = client.recv(1024)

                    while(True):
                        if msgReceived.decode() == "CorruptACK":
                            printACK(msgReceived)

                            for packet in window_packet:
                                _socket.send(packet)
                                time.sleep(0.01)
                        elif msgReceived.decode().startswith("ACK"):
                            # Split the message into indicidual acknowledgments
                            ack_num = msgReceived.decode().split('ACK')[-1:]
                            ack_num = int(ack_num[0])

                            if ack_num == seq_num:
                                window_packet.clear()
                                print("Set of 10 packets recieved")
                                break

    except IOError:     # if an error was encountered when reading from the file, we will error out
        print("You entered an invalid filename\n")
        print("Please enter a valid name. Eg 'filename.txt'")

if __name__ == '__main__':
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
                sendFile(file, client)

    except socket.error as e:
        # Return error file if and error occured creating or using the socket
        print(f"Could not connect to the server: {e}")

