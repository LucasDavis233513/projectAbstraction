# File server protocol
*Goal:* To send or request files between a server and a set of clients

## TODO
- Implement a proper sliding window
- Write a server side log to a file for a history of what each connected 
   client requested from the server
- Implement security to restrict access to the server and encrypt in flight
   packets
- Thread pool to limit number of connected clients and to handle their
   request simultaneously
- A GUI interface for the Client applicaiton (Server side will remain in a 
   CLI interface)
