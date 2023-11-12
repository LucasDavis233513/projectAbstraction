import os
import socket
import time

def checkSum(_data):
    checksum = 0
    # Convert a list of bytes into a list of integers by list comprehension
    # Takes two bytes from the data list and converts it to an integer with little-endian order.
    #   Least significant byte comes firts
    _data = [int.from_bytes(_data[i:i+2], 'little') for i in range(0, len(_data), 2)]

    # Iterate over the new list of int.
    for data16 in _data:
        checksum += data16

        # Run if the checksum is larger than 2^16
        #   right-shifting checksum by 16 and checking if the result is greater than 0
        while ((checksum >> 16) > 0):
            # Bitwise AND of checksuma and 0xFFFF (65535 or 2^16)
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

    # ~ bitwise NOT operator to flip the bits of checksum\
    # This with 0xFFFF to keep only the lowest 16 bits of checksum
    checksum = ~checksum & 0xFFFF

    return checksum

# Calculate the checksum on the data segment, and append it and the seq_num to the data
# to create our data packet: both are encoded using little endian 
def createPacket(_data, _seqNum):
    checksum = checkSum(_data)
    return _seqNum.to_bytes(2, 'little') + checksum.to_bytes(2, 'little') + _data

# Break the file into 1458 byte chunks of data create individual packets with this
# Data and append themp to a window buffer.
def fillWindowBuffer(_socket, filename):
    try:              
        seqNum = 0                      # Initialize the sequence number
        windowBuffer = []               # Create a window buffer to sotre the packets
        _socket.settimeout(5.0)         # Set the timeout to 5 seconds

        with open(filename, "rb") as fi:
            # Send the filename to the server if we are able to open the file
            _socket.send(filename.encode()) 

            while True:
                data = fi.read(1458)    # Read the file in chucks of 1458 bytes

                # If data is NULL (all bytes are read) break from the while loop
                if not data:
                    # Append the EOF flag to the end of the window buffer
                    windowBuffer.append("EOF".encode())
                    break

                # Create our packet
                # Append the data to the window buffer
                packet = createPacket(data, seqNum)
                windowBuffer.append(packet)

                # Increment seqNum
                seqNum += 1
            
            return windowBuffer
    # Return None if we have an invalid Filename
    except IOError:
        print("invalid Filename")
        return None

# printACK to the terminal for debugging purposes
def printACK(_ack):
    # if the server did not return a file, exit client program
    # As the connection is likely lost
    if not _ack:
        print("Server did not recieve file, or ACK didn't return")
        print("Connection to the server has been lost. Restart of the")
        print("Client is required")
        exit(1)
    else:
        # Print the reply
        print("%s\n"%_ack.decode())

# Logic to send the data in the window buffer to the sever using a 'sliding
# window' and the 'go-back-n' protocol
def sendFile(_socket, _windowBuffer, _base):
    # If there isn't any data in our _windowBuffer return
    if not _windowBuffer:
        print("The buffer is empty! Returning to main")
        return


# Main loop for client application
if __name__ == '__main__':
    file = ""
    host = "192.168.1.25"
    port = 32007
    
    # Create a socket using the internet address family IPv4, and specify we wish to
    #   Use the TCP protocol
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to the server
        client.connect((host, port))

        while(True):
            file = input("What is the files name: ")

            # interprate the given cmd, if exit close the client, if kill close both server and client
            #   Otherwise call the handleFile method and pass the socket and filename
            if(file == "exit"):
                client.close()
                exit(0)
            elif(file == "kill"):        
                client.send(file.encode())      # send the kill cmd
                ack = client.recv(1024)         # wait for ACK
                printACK(ack)                   # print the ACK                    

                exit(0)
            
            # Calculate the total number of packets based on file_size
            # Then determin the maximum window size
            file_size = os.path.getsize(file)
            total_packets = (file_size + 1457) // 1458
            WINDOW_SIZE = min(total_packets, 50)

            client.send(str(WINDOW_SIZE).encode())

            dataBuffer = fillWindowBuffer(client, file)
            sendFile(client, dataBuffer, 0)
    # Return error file if and error occured creating or using the socket
    except socket.error as e:
        print(f"Could not connect to the server: {e}")