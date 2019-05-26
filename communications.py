import socket
from time import sleep
from threading import Thread
import struct
import numpy as np


########################################################################
## Data encoding ##
###################

ACCELEROMETER_ID = 1
GYROSCOPE_ID = 2
GPS_ID = 3
BAROMETER_ID = 4
DATA_SOURCE_BYTES = [ACCELEROMETER_ID, GYROSCOPE_ID, GPS_ID, BAROMETER_ID]

# The maximum size of an individual packet
MAX_PACKET_SIZE = 1024
# The maximum number of ints encoded by an individual packet
#  = 255 as the number of ints is encoded by the single length byte (max value 255)
MAX_NUM_INTS = 255

def encode(data_source, data):
    # Packet format
    # '!BBii....'
    #
    # !: Set network byte alignment
    # B: Source byte (see DATA_SOURCE_BYTES)
    # B: Length byte - gives the number of integers that follow in data
    # i..: Data (of the number of integers given by length byte)

    # Set source byte
    if data_source in DATA_SOURCE_BYTES:
        source_byte = data_source
    else:
        raise Exception("Data source {} not recognised (must be one of {})".format(data_source, DATA_SOURCE_BYTES))

    # Set length byte
    length_byte = data.size
    if length_byte > MAX_NUM_INTS:
       raise Exception("Data is too long ({} ints > max number of ints, {})".format(length_byte, MAX_NUM_INTS))

    # Create format string: '!BBiiiii...'
    format_string = '!BB' + length_byte*'i'
    # Assemble packet ('\xSS\xLL\xDDDDD..')
    if length_byte > 1:
        packet = struct.pack(format_string, source_byte, length_byte, *data)
    else:
        packet = struct.pack(format_string, source_byte, length_byte, data)

    if struct.calcsize(format_string) > MAX_PACKET_SIZE:
        raise Exception("Packet too long ({} bits > max packet size {} bits)".format(struct.calcsize(format_string), MAX_PACKET_SIZE))

    return packet

def decode(buffer):
    # Packet format
    # '!BBii....'
    #
    # !: Set network byte alignment
    # B: Source byte (see DATA_SOURCE_BYTES)
    # B: Length byte - gives the number of integers that follow in data
    # i..: Data (of the number of integers given by length byte)

    # Second byte is data length
    length = packet[1]
    # Extract the data
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

    def receive_packet(self):
       packet = self.client.recv(MAX_PACKET_SIZE)
       if packet:
           return decode(packet)


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

    def receive_packet(self):
       packet = self.server.recv(MAX_PACKET_SIZE)
       if packet:
           return decode(packet)


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
                print(client.receive_packet())

        print("Mode not recognised.")
