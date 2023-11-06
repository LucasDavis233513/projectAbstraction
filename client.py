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

def sendFile(_socket,_file):
    try:
        base = 0
        seq_num = 0                         # Initialize the sequence numer
        window = []                         # Create a slinding window buffer to store the packets
        _socket.settimeout(5.0)             # Set the timeout to 5 seconds

        # Attempt to open file with read bytes option.
        with open(_file, "rb") as fi:
            _socket.send(_file.encode())  # Send the filename to the server

            while True:
                data = fi.read(1024) #read the file in chunks of 1024 bytes
                
                # If data is NULL (all bytes are read) break from the while loop
                if not data:        
                    _socket.send("EOF".encode())      # send an EOF message
                    ack = _socket.recv(1024)          # wait for final ACK message
                    printACK(ack)                     # print ACK
                    break

                # Calculate the checksum on the data segment, and append it and the seq_num to the data
                # to create our data packet: both are encoded using little endian 
                # Once we have our packet we will append it to the slinding window buffer
                checksum = checkSum(data)
                packet_to_send =  seq_num.to_bytes(2, 'little') + data + checksum.to_bytes(2, 'little')
                window.append(packet_to_send)

                # increment seq_num
                seq_num += 1

                # Once 10 packets have been appended to the buffer we will start to send each to the sever
                #   Once sent we will wait for an ACK from the server for the bundle of 10 packets
                if len(window) == WINDOW_SIZE or not data:
                    for packet in window[base:]:
                        _socket.send(packet)
                        time.sleep(0.01)

                    while True:
                        try:
                            ack = _socket.recv(1024)

                            if ack.decode() == "CorruptACK":
                                print("CorruptACK received, resending data")
                                for packet in window[base:]:
                                    _socket.send(packet)
                                    time.sleep(0.01)
                                continue
                            
                            ack_num = int(ack.decode().split('ACK')[-1])

                            if ack_num >= base:
                                base = ack_num + 1
                            break
                        except socket.timeout:
                            print("timeout occured, resending data")
                            continue
                        except (ValueError, IndexError):
                            print("Invalid ACK received")
                            continue

                    window = window[base:]
                    base = 0

    # if an error was encountered when reading from the file, we will error out
    except IOError:     
        print("invalid filename")
        exit(1)

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
            #   Otherwise call the sendFile method and pass the socket and filename
            if(file == "exit"):
                client.close()
                exit(0)
            elif(file == "kill"):        
                client.send(file.encode())      # send the kill cmd
                ack = client.recv(1024)         # wait for ACK
                printACK(ack)                   # print the ACK                    

                exit(0)
            else:
                file_size = os.path.getsize(file)
                total_packets = (file_size + 1023) // 1024
                WINDOW_SIZE = min(total_packets, 50)

                client.send(str(WINDOW_SIZE).encode())

                sendFile(client, file)
    # Return error file if and error occured creating or using the socket
    except socket.error as e:
        print(f"Could not connect to the server: {e}")