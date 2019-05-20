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
## L3GD20H Commands ##
######################
# ODR
LGD_SET_ODR = {12.5:0b00001111, # 12.5Hz
               25 : 0b01001111, # 25Hz
               50 : 0b10001111} # 50Hz
# Scale
LGD_SET_SCALE = {245: 0b00000000, #+/- 245dps
                 500: 0b00010000, #+/- 500dps
                 2000:0b00100000} #+/- 2000dps

# Sensitivity
# raw value * sensitivity = value
LGD_SENS = {245: 8.75e-3, # dps/digit # for 245dps scale
            500: 17.5e-3, # dps/digit # for 500dps scale
            2000:70.0e-3} # dps/digit # for 2000dps scale


########################################################################
## Gyroscope Class ##
#####################
class Gyroscope:
	def __init__(self, bus, odr=50, scale=245):
		self.bus = bus
		self.odr = odr
		self.scale = scale
		self.sens = LGD_SENS[scale]

		if self.bus.read_byte_data(LGD, LGD_WHOAMI_ADDRESS) != LGD_WHOAMI_CONTENTS:
			raise Exception("LGD not found at address {}.".format(LGD))
		else:
			# Enable gyro axes and set ODR
			self.bus.write_byte_data(LGD, LGD_CTRL_1, LGD_SET_ODR[self.odr])
			# Set scale
			self.bus.write_byte_data(LGD, LGD_CTRL_4, LGD_SET_SCALE[self.scale])
			print("Gyroscope set up.")

	def read(self):
		x_L = self.bus.read_byte_data(LGD, LGD_OUT_X_L)
		x_H = self.bus.read_byte_data(LGD, LGD_OUT_X_H)
		y_L = self.bus.read_byte_data(LGD, LGD_OUT_Y_L)
		y_H = self.bus.read_byte_data(LGD, LGD_OUT_Y_H)
		z_L = self.bus.read_byte_data(LGD, LGD_OUT_Z_L)
		z_H = self.bus.read_byte_data(LGD, LGD_OUT_Z_H)
		self.x = (x_H << 8 | x_L) * self.sens
		self.y = (y_H << 8 | y_L) * self.sens
		self.z = (z_H << 8 | z_L) * self.sens
		return (self.x, self.y, self.z)

########################################################################
## Main ##
##########
if __name__ == "__main__":
	from smbus import SMBus
	from time import sleep

	# Initialise the i2c bus
	I2CBUS_NUMBER = 1
	bus = SMBus(I2CBUS_NUMBER)

	# Initialise the gyroscope
	gyroscope1 = Gyroscope(bus)

	try:
		while True:
			print(gyroscope1.read())
			sleep(1/3)
			#sleep(1/50)
	except KeyboardInterrupt:
		print("Exiting...")

