########################################################################
## LSM303D register addresses ##
################################
# For reference see www.pololu.com/file/0J703/LSM303D.pdf

# Device i2c address
LSM = 0x1D

# Device self-identification
LSM_WHOAMI_ADDRESS = 0x0F
LSM_WHOAMI_CONTENTS = 0b1001001

# Control registers
LSM_CTRL_0 = 0x1F # General settings
LSM_CTRL_1 = 0x20 # Turns on accelerometer and configures data rate
LSM_CTRL_2 = 0x21 # Self test accelerometer, anti-aliasing accel filter
LSM_CTRL_3 = 0x22 # Interrupts
LSM_CTRL_4 = 0x23 # Interrupts
LSM_CTRL_5 = 0x24 # Turns on temperature sensor
LSM_CTRL_6 = 0x25 # Magnetic resolution selection, data rate config
LSM_CTRL_7 = 0x26 # Turns on magnetometer and adjusts mode

# Magnetometer output registers
LSM_MAG_X_L = 0x08
LSM_MAG_X_H = 0x09
LSM_MAG_Y_L = 0x0A
LSM_MAG_Y_H = 0x0B
LSM_MAG_Z_L = 0x0C
LSM_MAG_Z_H = 0x0D

# Accelerometer output registers
LSM_ACC_X_L = 0x28
LSM_ACC_X_H = 0x29
LSM_ACC_Y_L = 0x2A
LSM_ACC_Y_H = 0x2B
LSM_ACC_Z_L = 0x2C
LSM_ACC_Z_H = 0x2D

# Temperature output registers
LSM_TEMP_L = 0x05
LSM_TEMP_H = 0x06

# For further control registers (offsets, references, FIFO, interrupts, 
# etc), see datasheet

########################################################################
## Initialisation functions ##
##############################

def initialise():
	global bus
	if bus.read_byte_data(LSM, LSM_WHOAMI_ADDRESS) != LSM_WHOAMI_CONTENTS:
		raise Exception("LSM not found at address {}.".format(LSM))
	else:
		# Enable accelerometer axes and set ODR (output data rate) = 50 Hz
		bus.write_byte_data(LSM, LSM_CTRL_1, 0b01010111)
		# Set acceleration full-scale to +/-2g
		bus.write_byte_data(LSM, LSM_CTRL_2, 0b00000000)
		# Disable thermometer, set magnetic resolution high, ODR 50Hz
		bus.write_byte_data(LSM, LSM_CTRL_5, 0b01110000)
		# Set magnetic full-scale to +/- 4 gauss
		bus.write_byte_data(LSM, LSM_CTRL_6, 0b00100000)
		# Set magnetometer low power mode off
		bus.write_byte_data(LSM, LSM_CTRL_7, 0b00000000)
		print("Accelerometer/magnetometer set up.")

########################################################################
## Read functions ##
####################

def read_accelerometer():
	global bus
	x_L = bus.read_byte_data(LSM, LSM_ACC_X_L)
	x_H = bus.read_byte_data(LSM, LSM_ACC_X_H)
	y_L = bus.read_byte_data(LSM, LSM_ACC_Y_L)
	y_H = bus.read_byte_data(LSM, LSM_ACC_Y_H)
	z_L = bus.read_byte_data(LSM, LSM_ACC_Z_L)
	z_H = bus.read_byte_data(LSM, LSM_ACC_Z_H)
	x = x_H << 8 | x_L
	y = y_H << 8 | y_L
	z = z_H << 8 | z_L
	return (x, y, z)

def read_magnetometer():
	global bus
	x_L = bus.read_byte_data(LSM, LSM_MAG_X_L)
	x_H = bus.read_byte_data(LSM, LSM_MAG_X_H)
	y_L = bus.read_byte_data(LSM, LSM_MAG_Y_L)
	y_H = bus.read_byte_data(LSM, LSM_MAG_Y_H)
	z_L = bus.read_byte_data(LSM, LSM_MAG_Z_L)
	z_H = bus.read_byte_data(LSM, LSM_MAG_Z_H)
	x = x_H << 8 | x_L
	y = y_H << 8 | y_L
	z = z_H << 8 | z_L
	return (x, y, z)
	
########################################################################
## Main ##
##########
if __name__ == "__main__":
	from smbus import SMBus
	from time import sleep
	
	# Initialise the i2c bus
	I2CBUS_NUMBER = 1
	bus = SMBus(I2CBUS_NUMBER)
	initialise()
	for a in range(500):
		print(read_accelerometer())
		print(read_magnetometer())
		print("")
		sleep(1/50)

