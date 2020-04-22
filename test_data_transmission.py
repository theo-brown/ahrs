import communications as com
from smbus import SMBus
from gyroscope import Gyroscope
from accelerometer import Accelerometer
from barometer import Barometer
from gps import GPSSensor

import numpy as np
from time import sleep

# Initialise the i2c bus
I2CBUS_NUMBER = 1
bus = SMBus(I2CBUS_NUMBER)

# Initialise the gyroscope
gyroscope1 = Gyroscope(bus)

# Initialise the accelerometer
accelerometer1 = Accelerometer(bus)

# Initialise the barometer
barometer1 = Barometer(bus)
barometer1.calibrate()

# Initialise the GPS
gps1 = GPSSensor()
gps1.initialise()

# Initialise the server
server = com.ServerSocket()
server.connect()

try:
    while True:
        server.write(com.ACCELEROMETER_ID, np.asarray(accelerometer1.read_acc()))
        server.write(com.MAGNETOMETER_ID, np.asarray(accelerometer1.read_mag()))
        server.write(com.GYROSCOPE_ID, np.asarray(gyroscope1.read()))
        server.write(com.BAROMETER_ID, np.asarray(barometer1.read_relative_altitude()))
        server.write(com.GPS_ID, np.asarray([gps1.lat, gps1.lon]))
        sleep(1/25)

except KeyboardInterrupt:
    print("Exiting...")
