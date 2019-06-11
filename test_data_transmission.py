import communications as com
from smbus import SMBus
from gyroscope import Gyroscope
from accelerometer import Accelerometer
import numpy as np
from time import sleep

# Initialise the i2c bus
I2CBUS_NUMBER = 1
bus = SMBus(I2CBUS_NUMBER)

# Initialise the gyroscope
gyroscope1 = Gyroscope(bus)

# Initialise the accelerometer
accelerometer1 = Accelerometer(bus)

# Initialise the server
server = com.ServerSocket()
server.connect()

try:
    while True:
        #data = gyroscope1.read()
        data = accelerometer1.read_acc()
        print(data)
        #server.write(com.GYROSCOPE_ID, np.asarray(data))
        server.write(com.ACCELEROMETER_ID, np.asarray(data))
        sleep(1/25)

except KeyboardInterrupt:
    print("Exiting...")
