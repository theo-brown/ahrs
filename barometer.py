########################################################################
## Imports ##
#############
import numpy as np

########################################################################
## Global variables ##
######################
zero_value = 0

########################################################################
## LPS331AP register addresses ##
#################################
# For reference see www.pololu.com/file/0J622/LPS331AP.pdf

# Device i2c address
LPS = 0x5D

# Device self-identification
LPS_WHOAMI_ADDRESS = 0x0F
LPS_WHOAMI_CONTENTS = 0b10111011

# Reference presure registers
LPS_REF_P_XL = 0x08
LPS_REF_P_L = 0x09
LPS_REF_P_H = 0x0A

# Control registers
LPS_RES_CONF = 0x10 # Resolution mode configuration
LPS_CTRL_1 = 0x20
LPS_CTRL_2 = 0x21
LPS_CTRL_3 = 0x22
LPS_INT_CFG = 0x23 # Interrupt configuration
LPS_INT_SOURCE = 0x24 # Interrupt source
LPS_THS_P_LOW = 0x25 # Threshold pressure (LSB)
LPS_THS_P_HIGH = 0x26 # Threshold pressure (MSB)
LPS_STATUS = 0x27 # Status register

# Pressure output registers
LPS_PRESS_OUT_XL = 0x28 # LSB
LPS_PRESS_OUT_L = 0x29
LPS_PRESS_OUT_H = 0x2A # MSB

# Temperature output registers
LPS_TEMP_OUT_L = 0x2B # LSB
LPS_TEMP_OUT_H = 0x2C # MSB

# Other
LPS_AMP_CTRL = 0x30

########################################################################
## Initialisation functions ##
##############################

def initialise():
	global bus
	if bus.read_byte_data(LPS, LPS_WHOAMI_ADDRESS) != LPS_WHOAMI_CONTENTS:
		raise Exception("LPS not found at address {}.".format(LPS))
	else:
		# Enable barometer and set ODR 25 Hz
		bus.write_byte_data(LPS, LPS_CTRL_1, 0b11000000)


########################################################################
## Read functions ##
####################

def read_raw():
	global bus
	# Read from registers
	pressure_XL = bus.read_byte_data(LPS, LPS_PRESS_OUT_XL)
	pressure_L = bus.read_byte_data(LPS, LPS_PRESS_OUT_L)
	pressure_H = bus.read_byte_data(LPS, LPS_PRESS_OUT_H)
	# Convert to bytes
	pressure_b = pressure_H << 16 | pressure_L << 8 | pressure_XL
	return pressure_b

def calibrate():
	global bus
	global zero_value
	num_datapoints = 1000
	calibration_data = np.zeros(num_datapoints)
	print("Calibrating barometer...")
	print("Place the sensor on the ground.")
	for i in np.arange(num_datapoints):
		calibration_data[i] = read_raw()
	print("Calibration successful.")
	zero_value = int(np.mean(calibration_data))

def read_relative():
	global bus, zero_value
	return read_raw() - zero_value


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
	calibrate()
	for a in range(500):
		print(read_relative())
		sleep(1/50)
