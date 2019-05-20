########################################################################
## Imports ##
#############
import numpy as np

########################################################################
## LPS331AP register addresses ##
#################################
# For reference see www.pololu.com/file/0J622/LPS331AP.pdf

# Device i2c address
LPS = 0x5D

# Device self-identification
LPS_WHOAMI_ADDRESS = 0x0F
LPS_WHOAMI_CONTENTS = 0b10111011

# Reference pressure registers
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
## LPS331AP Commands ##
#######################
# ODR
LPS_SET_ODR = {12.5:0b11100000, # 12.5Hz
               25 : 0b11110000} # 25Hz


########################################################################
## Barometer class ##
#####################
class Barometer:
	def __init__(self, bus, odr=12.5, calibration_num_datapoints=1000):
		self.bus = bus
		self.odr = odr
		self.calibration_num_datapoints = calibration_num_datapoints
		self.pressure_datum = 0
		self.altitude_datum = 0

		if self.bus.read_byte_data(LPS, LPS_WHOAMI_ADDRESS) != LPS_WHOAMI_CONTENTS:
			raise Exception("LPS not found at address {}.".format(LPS))
		else:
			# Enable barometer and set ODR 25 Hz
			self.bus.write_byte_data(LPS, LPS_CTRL_1, LPS_SET_ODR[self.odr])
			print("Barometer set up.")

	def read(self):
		# Read pressure from registers
		pressure_XL = self.bus.read_byte_data(LPS, LPS_PRESS_OUT_XL)
		pressure_L = self.bus.read_byte_data(LPS, LPS_PRESS_OUT_L)
		pressure_H = self.bus.read_byte_data(LPS, LPS_PRESS_OUT_H)
		# Update stored pressure values in mbar see datasheet for formula
		self.pressure = (pressure_H << 16 | pressure_L << 8 | pressure_XL) / 4096.0
		self.relative_pressure = self.pressure - self.pressure_datum
		# Update the stored altitude value
		self.altitude = 44308.7 * (1 - ((self.pressure/1013.25)**0.190284))
		self.relative_altitude = self.altitude - self.altitude_datum
		# Return absolute pressure value
		return self.pressure

	def read_relative_pressure(self):
		# Update all stored pressure/altitude values
		self.read()
		# Return the relative pressure value
		return self.relative_pressure

	def read_altitude(self):
		# Update all stored pressure/altitude values
		self.read()
		# Return altitude
		return self.altitude

	def read_relative_altitude(self):
		# Update all stored pressure/altitude values
		self.read()
		# Return altitude
		return self.relative_altitude

	def calibrate(self):
		pressure_data = np.zeros(self.calibration_num_datapoints)
		altitude_data = np.zeros(self.calibration_num_datapoints)

		print("Calibrating barometer...")
		print("Place the sensor on the ground.")
		for i in np.arange(self.calibration_num_datapoints):
			pressure_data[i] = self.read()
			altitude_data[i] = self.read_altitude()
		# Calculate average value (TODO: replace with a fancy filter)
		self.pressure_datum = np.mean(pressure_data)
		self.altitude_datum = np.mean(altitude_data)
		# Update stored values
		self.read()
		print("Calibration successful.")


########################################################################
## Main ##
##########
if __name__ == "__main__":
	from smbus import SMBus
	from time import sleep

	# Initialise the i2c bus
	I2CBUS_NUMBER = 1
	bus = SMBus(I2CBUS_NUMBER)

	# Initialise the barometer
	barometer1 = Barometer(bus)
	barometer1.calibrate()

	try:
		while True:
			print(barometer1.read_relative_altitude())
			sleep(1/25)
	except KeyboardInterrupt:
		print("Exiting...")
