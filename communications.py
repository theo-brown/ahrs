import socket
import struct
import numpy as np
import errno
import time

########################################################################
## Data encoding ##
###################
# Packet format
# '!BBff....'
#
# !: Set network byte alignment
# B: Packet length byte
# B: Data source byte (see DATA_SOURCE_BYTES)
# f..: Data (floats)
HEADER_FORMAT = '!BB'
HEADER_LENGTH = len(HEADER_FORMAT) - 1  # -1 as the ! is formatting rather than transmitted data

PACKET_LENGTH_BYTE = 0  # Location of packet length byte
DATA_SOURCE_BYTE = 1  # Location of data source byte
FIRST_DATA_BYTE = 2  # Location of first data byte

ACCELEROMETER_ID = 1
MAGNETOMETER_ID = 2
GYROSCOPE_ID = 3
GPS_ID = 4
BAROMETER_ID = 5
DATA_SOURCE_BYTES = [ACCELEROMETER_ID, MAGNETOMETER_ID, GYROSCOPE_ID, GPS_ID, BAROMETER_ID]

VALUE_SIZE = 4  # Number of bytes used to store a float

READ_BUFFER_SIZE = 1024


def encode(data_source, data):
    # Set source byte
    if data_source in DATA_SOURCE_BYTES:
        source_byte = data_source
    else:
        raise Exception("Data source {} not recognised (must be one of {})"
                        .format(data_source, DATA_SOURCE_BYTES))

    # If it's a scalar, size is 1
    if np.ndim(data) == 0:
        size = 1
    # If it's an array, grab the size
    elif isinstance(data, np.ndarray):
        size = data.size
    else:
        raise Exception("Data type not recognised (must be scalar or ndarray)")

    # Create format string: '!BBfffff...'
    format_string = HEADER_FORMAT + size*'f'

    # Assemble packet
    if size > 1:
        # Need to unzip the array
        packet = struct.pack(format_string,
                             size*VALUE_SIZE+HEADER_LENGTH,
                             source_byte,
                             *data)
    else:
        packet = struct.pack(format_string,
                             size*VALUE_SIZE+HEADER_LENGTH,
                             source_byte,
                             data)

    return packet


def decode(packet):
    if packet:
        # Extract header data
        packet_length = packet[PACKET_LENGTH_BYTE]
        data_source = packet[DATA_SOURCE_BYTE]

        number_of_values = (packet_length - HEADER_LENGTH)//VALUE_SIZE

        # Extract the data
        format_string = '!' + 'f'*number_of_values
        data = struct.unpack(format_string, packet[FIRST_DATA_BYTE:])

        return packet_length, data_source, np.asarray(data)


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
        try:
            self.buffer = self.connection.recv(READ_BUFFER_SIZE)
        except socket.error as e:
            self.buffer = b''
            # Connection reset error
            # TODO: I don't think this works
            if e.errno == errno.ECONNRESET:
                print("Connection reset. Attempting to reconnect...")
                self.connect()
            # All other errors
            else:
                raise

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
        packet_length = self.buffer[PACKET_LENGTH_BYTE]

        # If the whole packet is in the buffer, extract it
        if len(self.buffer) >= packet_length:
            # Remove the packet from the buffer
            packet = self.buffer[:packet_length]
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
    def __init__(self, server_address='192.168.42.1', server_port=12345,
                 retry_connection=True, timeout=3):
        super().__init__()
        self.server_port = server_port
        self.server_address = server_address
        self.retry_connection = retry_connection
        self.timeout = timeout

    def connect(self):
        try:
            print("Connecting to server...")

            self.socket.connect((self.server_address, self.server_port))

            print("Socket connected to server at {}:{}"
                  .format(self.server_address, self.server_port))

        except Exception as e:
            print("Exception ocurred: {}".format(Exception))

            if self.retry_connection:
                if not hasattr(self, 'start_time'):
                    self.start_time = time.time()

                print("Retrying.")

                while (time.time() - self.start_time) < self.timeout:
                    self.connect()


########################################################################
if __name__ == '__main__':
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
