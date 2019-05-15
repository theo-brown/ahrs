########################################################################
## L3GD20H register addresses ##
################################
# For reference see www.pololu.com/file/0J731/L3GD20H.pdf

# Device i2c address
LGD = 0x6B

# Device self-identification
LGD_WHOAMI_ADDRESS = 0x0F
LGD_WHOAMI_CONTENTS = 0b11010111

# Control registers
LGD_CTRL_1 = 0x20 # Turns on gyro
LGD_CTRL_2 = 0x21 # Sets a high-pass filter for gyro
LGD_CTRL_3 = 0x22
LGD_CTRL_4 = 0x23
LGD_CTRL_5 = 0x24
LGD_REFERENCE = 0x25

# Temperature output register
LGD_OUT_TEMP = 0x26

# Status register
LGD_STATUS = 0x27

# Gyroscope output registers
LGD_OUT_X_L = 0x28
LGD_OUT_X_H = 0x29
LGD_OUT_Y_L = 0x2A
LGD_OUT_Y_H = 0x2B
LGD_OUT_Z_L = 0x2C
LGD_OUT_Z_H = 0x2D

# For further control registers (FIFO, interrupts, etc), see datasheet

########################################################################
## Initialisation functions ##
##############################

def initialise():
	global bus
	if bus.read_byte_data(LGD, LGD_WHOAMI_ADDRESS) != LGD_WHOAMI_CONTENTS:
		raise Exception("LGD not found at address {}.".format(LGD))
	else:
		# Enable gyro axes and set ODR 50Hz
		bus.write_byte_data(LGD, LGD_CTRL_1, 0b10001111)
		print("Gyroscope set up.")


########################################################################
## Read functions ##
####################

def read():
	global bus
	x_L = bus.read_byte_data(LGD, LGD_OUT_X_L)
	x_H = bus.read_byte_data(LGD, LGD_OUT_X_H)
	y_L = bus.read_byte_data(LGD, LGD_OUT_Y_L)
	y_H = bus.read_byte_data(LGD, LGD_OUT_Y_H)
	z_L = bus.read_byte_data(LGD, LGD_OUT_Z_L)
	z_H = bus.read_byte_data(LGD, LGD_OUT_Z_H)
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
		print(read())
		sleep(1/50)

