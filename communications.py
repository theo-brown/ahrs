import socket
from time import sleep
from threading import Thread
import struct
import numpy as np


########################################################################
## Data encoding ##
###################
# Packet format
# '!BBii....'
#
# !: Set network byte alignment
# B: Packet length byte
# B: Data source byte (see DATA_SOURCE_BYTES)
# i..: Data (integers)
HEADER_FORMAT = '!BB'
HEADER_LENGTH = len(HEADER_FORMAT) - 1 # -1 as the ! is formatting rather than transmitted data

ACCELEROMETER_ID = 1
GYROSCOPE_ID = 2
GPS_ID = 3
BAROMETER_ID = 4
DATA_SOURCE_BYTES = [ACCELEROMETER_ID, GYROSCOPE_ID, GPS_ID, BAROMETER_ID]

INT_SIZE = 4 # Number of bytes used to store an int

READ_BUFFER_SIZE = 1024

def encode(data_source, data):
    # Set source byte
    if data_source in DATA_SOURCE_BYTES:
        source_byte = data_source
    else:
        raise Exception("Data source {} not recognised (must be one of {})".format(data_source, DATA_SOURCE_BYTES))

    # Create format string: '!BBiiiii...'
    format_string = HEADER_FORMAT + data.size*'i'

    # Assemble packet
    if data.size > 1:
        packet = struct.pack(format_string, data.size*INT_SIZE+HEADER_LENGTH, source_byte, *data)
    else:
        packet = struct.pack(format_string, data.size*INT_SIZE+HEADER_LENGTH, source_byte, data)

    return packet

def decode(packet):
    if packet:
        # Find the length of the data byte (the first byte minus the header length)
        number_of_ints = (packet[0] - HEADER_LENGTH)//INT_SIZE
        # Extract the data
        format_string = HEADER_FORMAT + 'i'*number_of_ints
        packet_length, data_source, data = struct.unpack(format_string, packet)

        return packet_length, data_source, np.array(data)

########################################################################
## Streaming socket ##
######################
class StreamingSocket:
    def __init__(self):
        self.part_packet = b''
        self.read_buffer = b''

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Default connection is the socket itself (client mode)
        # For server mode, set self.connection = self.socket.accept()[0]
        self.connection = self.socket

    def read(self):
        self.buffer = self.connection.recv(READ_BUFFER_SIZE)
        self.received_packets = []
        while self.buffer:
            self.received_packets.append(decode(self.read_packet_from_buffer()))
        return self.received_packets

    def read_packet_from_buffer(self):
        # If the buffer's empty, return empty
        if not self.buffer:
            return b''

        # Append any existing part packet to the beginning of the buffer
        if self.part_packet:
            self.buffer = b''.join([self.part_packet, self.buffer])
            # Clear the part_packet variable
            self.part_packet = b''

        # Extract the length of the first packet from the buffer
        packet_length = self.buffer[0]

        # If the whole packet is in the buffer, extract it
        if len(self.buffer) >= packet_length:
            # Remove the packet from the buffer
            packet = self.buffer[0:packet_length]
            self.buffer = self.buffer[packet_length:]
            return packet

        else:
            # Save the part packet for later
            self.part_packet = self.buffer
            # Empty the buffer
            self.buffer = b''
            # Return empty
            return b''

    def write(self, data_source, data):
        packet = encode(data_source, data)
        self.connection.send(packet)

    def connect(self):
        return

########################################################################
## Server socket ##
###################
class ServerSocket(StreamingSocket):
    def __init__(self, port=12345):
        super().__init__()
        self.port = port
        self.socket.bind(('', self.port))
        self.socket.listen()

    def connect(self):
        # Connect to a client
        print("Waiting for client connection...")
        self.connection, self.client_address = self.socket.accept()
        print("Socket connected to client at {}".format(self.client_address))


########################################################################
## Client socket ##
###################
class ClientSocket(StreamingSocket):
    def __init__(self, server_address='192.168.42.1', server_port=12345):
        super().__init__()
        self.server_port = server_port
        self.server_address = server_address

    def connect(self):
        self.socket.connect((self.server_address, self.server_port))
        print("Socket connected to server at {}:{}".format(self.server_address, self.server_port))

########################################################################
if __name__=='__main__':
    while True:
        mode = input("Select mode [s]erver/[c]lient: ")

        if mode == 's':
            server = ServerSocket()
            server.connect()
            a = 1
            while True:
               print(server.write(ACCELEROMETER_ID, np.asarray(a)))
               a = (a+1) % 32768
               print(server.read())

        elif mode == 'c':
            client = ClientSocket()
            client.connect()
            while True:
                print(client.read())
                print(client.write(GYROSCOPE_ID, np.asarray(1)))

        print("Mode not recognised.")
