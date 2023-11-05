import socket
import time

WINDOW_SIZE = 10

def checkSum(_data):
    checksum = 0
    _data = [int.from_bytes(_data[i:i+2], 'little') for i in range(0, len(_data), 2)]

    for data16 in _data:
        checksum += data16

        # while there is a carray
        while ((checksum >> 16) > 0):
            # Add cary to the sum
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

    # Ones complement
    checksum = ~checksum & 0xFFFF

    return checksum

def extractData(_data):    
    seq_number = int.from_bytes(_data[:2], 'little')  # Extract the first two bytes as the seq_number
    _data = _data[2:]                                 # remove the first two bytes
    checksum = int.from_bytes(_data[-2:], 'little')   # Extract the last two bytes as the checksum
    _data = _data[:-2]                                # remove the last two bytes
    return _data, checksum, seq_number

def recieveFile(_socket):
    data_buffer = []                            # create a data buffer array to store the file bytes
    window_packets = [None] * WINDOW_SIZE       # Create a window buffer to store the packets
    base = 0                                    # Initialize the base of the window

    while True:
        data = _socket.recv(1028)               # Wait for incoming data stream up to 1028 bytes in the reciver window
                                                # 4 bytes for seq_num and checksum and 1024 for data

        # Client sends a EOF message to inidicate the end of the data stream
        if data == b'EOF':
            print("File recieved")

            # Write all data in the buffer to a file.
            with open(filename, "wb") as fo:
                for data in data_buffer:
                    fo.write(data)

            # Clear the data buffer
            data_buffer.clear()
        
            _socket.send("File recieved".encode())
            time.sleep(0.01)

            break
        elif data:
            data, receivedCheckSum, recievedSeqNum = extractData(data)
            serverCheckSum = checkSum(data)                    # Calculate the checksum on recieved data

            # If recievedCheckSum is equal to the serverCheckSum 
            # add data to the window
            if receivedCheckSum == serverCheckSum:
                # Add received data to the window
                window_packets[recievedSeqNum % WINDOW_SIZE] = data

                # If the base packet has been received, write all packet sto the buffer 
                # and slide the window
                while window_packets[base % WINDOW_SIZE] is not None:
                    data_buffer.append(window_packets[base % WINDOW_SIZE])
                    window_packets[base % WINDOW_SIZE] = None
                    base += 1

                if base % 10 == 0:
                    clientSocket.send(f"ACK{base}".encode())
                time.sleep(0.01)
            else:   # otherwise send Corrupt ACK back to client
                _socket.send("CorruptACK".encode())
                time.sleep(0.01)
        else:
            break
    
if __name__ == '__main__':
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
            filename = clientSocket.recv(1024).decode() # Initial data will be the filename
            
            #If the filename is set to "kill" the server will close the clients connection and shutdown the server
            if filename == 'kill':
                clientSocket.send("ACKed, shutting Down Server".encode())

                print("Kill cmd received. Shutting down the server")

                clientSocket.close()
                server.close()
                exit(0) # Ext with status code 0
            else:
                recieveFile(clientSocket)

    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Server could not be started: {e}")
