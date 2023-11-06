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

def extractData(_data):
    seq_number = int.from_bytes(_data[:2], 'little')  # Extract the first two bytes as the seq_number
    _data = _data[2:]                                 # remove the first two bytes
    checksum = int.from_bytes(_data[-2:], 'little')   # Extract the last two bytes as the checksum
    _data = _data[:-2]                                # remove the last two bytes

    return _data, checksum, seq_number

def recieveFile(_socket, file):
    data_buffer = []                                  # create a data buffer array to store the file bytes
    excepted_seqNum = 0                               # Initialize the base of the window
    _socket.settimeout(5.0)                           # Set timeout to 5 seconds

    while True:
        # Try to get the data packet, if timeout send CorruptACK
        try:
            data = _socket.recv(1028)                 # Wait for incoming data stream up to 1028 bytes in the reciver window
        except socket.timeout:                        # 4 bytes for seq_num and checksum and 1024 for data
            print("Timeout orccurred, sending CorruptACK")
            _socket.send("CorruptACK".encode())
            continue

        # Client sends a EOF message to inidicate the end of the data stream
        if data == b'EOF':
            print("File recieved")

            # Write all data in the buffer to a file.
            with open(file, "wb") as fo:
                for data in data_buffer:
                    fo.write(data)

            # Clear the data buffer
            data_buffer.clear()
        
            # Send final ACK
            _socket.send("File recieved".encode())
            time.sleep(0.01)
            break
        else:
            data, recieved_checksum, recieved_seqNum = extractData(data)  # Extract the seq_num and checksum from packet

            if recieved_checksum == checkSum(data) and recieved_seqNum == excepted_seqNum:
                data_buffer.append(data)
                excepted_seqNum += 1
                _socket.send(f"ACK{excepted_seqNum}".encode())
            else:
                _socket.send("CorruptACK".encode())
    
if __name__ == '__main__':
    host = "192.168.1.25"
    port = 32007

    # Define our socket to use the Internet address family IPv4 and indicate
    #   That we want to use the TCP protocol
    # The following will allow us to reuse a local address 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Bind the IP address and the port number &
        # Listen for incoming connections
        # Accept an incoming connection and display its information to the screen
        server.bind((host, port))
        server.listen()
        (clientSocket, clientAdress) = server.accept()
        print("Connection from: " + str(clientAdress))

        while(True):
            # Set the timeout to none when waiting for a filename
            clientSocket.settimeout(None)

            WINDOW_SIZE = clientSocket.recv(1024).decode()

            # Accept and initial stream of data from the client
            #   The server is expecting the filename to be sent first
            filename = clientSocket.recv(1024).decode()
            
            # Interprate the recieved data. If it is a kill cmd shutdown the server
            #   else call the recieveFile method and pass the socket and filename
            if filename == 'kill':
                clientSocket.send("ACKed, shutting Down Server".encode())

                print("Kill cmd received. Shutting down the server")

                clientSocket.close()
                server.close()
                exit(0) # Ext with status code 0
            else:
                recieveFile(clientSocket, filename)

    except socket.error as e:
        # Return error message if and error occured creating or using the socket
        print(f"Server could not be started: {e}")