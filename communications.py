import socket
from time import sleep
from threading import Thread
import struct
import numpy as np


########################################################################
## Data encoding ##
###################
# Packet format
# '!BBii....c'
#
# !: Set network byte alignment
# B: Source byte (see DATA_SOURCE_BYTES)
# B: Length byte (number of integers in data)
# i..: Data (integers)
# c: end packet byte (END_BYTE)

ACCELEROMETER_ID = 1
GYROSCOPE_ID = 2
GPS_ID = 3
BAROMETER_ID = 4
DATA_SOURCE_BYTES = [ACCELEROMETER_ID, GYROSCOPE_ID, GPS_ID, BAROMETER_ID]

END_BYTE = b','

READ_BUFFER_SIZE = 1024

def encode(data_source, data):
    # Set source byte
    if data_source in DATA_SOURCE_BYTES:
        source_byte = data_source
    else:
        raise Exception("Data source {} not recognised (must be one of {})".format(data_source, DATA_SOURCE_BYTES))

    # Create format string: '!BBiiiii...c'
    format_string = '!BB' + data.size*'i' + 'c'
    # Assemble packet
    if data.size > 1:
        packet = struct.pack(format_string, source_byte, data.size, *data, END_BYTE)
    else:
        packet = struct.pack(format_string, source_byte, data.size, data, END_BYTE)

    return packet

def decode(packet):
    # Find the length byte (the second byte)
    length = packet[1]
    # Extract the data
    if packet[-1] == END_BYTE:
        format_string = '!BB' + 'i'*length + 'c'
        source, length, data, end_byte = struct.unpack(format_string, packet)
    else:
        format_string = '!BB' + 'i'*length
        source, length, data = struct.unpack(format_string, packet)

    return source, length, np.array(data)


########################################################################
## Server socket ##
###################
class ServerSocket:
    def __init__(self, port=12345):
        self.port = port

        # Create a server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of the address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the port
        self.server_socket.bind(('', self.port))
        # Listen for connections
        self.server_socket.listen()

    def wait_for_client_connection(self):
        # Connect to a client
        print("Waiting for client connection...")
        self.client, self.client_address = self.server_socket.accept()
        print("Connected to client at {}".format(self.client_address))

    def send_packet(self, data_source, data):
       packet = encode(data_source, data)
       self.client.send(packet)

    def receive(self):
       buffer = self.client.recv(READ_BUFFER_SIZE)
       if buffer:
           packets = buffer.split(END_BYTE)
           decoded_packets = np.asarray([decode(packet) for packet in packets if packet])
           return decoded_packets

########################################################################
## Client socket ##
###################
class ClientSocket:
    def __init__(self, server_address='192.168.42.1', server_port=12345):
        self.server_address = server_address
        self.server_port = server_port

        # Create the socket for connecting to the server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.server.connect((self.server_address, self.server_port))

    def send_packet(self, data_source, data):
       packet = encode(data_source, data)
       self.server.send(packet)

    def receive(self):
       buffer = self.server.recv(READ_BUFFER_SIZE)
       if buffer:
           packets = buffer.split(END_BYTE)
           decoded_packets = np.asarray([decode(packet) for packet in packets if packet])
           return decoded_packets


if __name__ == '__main__':
    while True:
        mode = input("Select mode [s]erver/[c]lient: ")

        if mode == 's':
            server = ServerSocket()
            server.wait_for_client_connection()
            a = 1
            while True:
               server.send_packet(ACCELEROMETER_ID, np.asarray(a))
               a = (a+1) % 32768

        elif mode == 'c':
            client = ClientSocket()
            client.connect()
            while True:
                print(client.receive())

        print("Mode not recognised.")
