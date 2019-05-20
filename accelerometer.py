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
## LSM303D Commands ##
######################
# ODR
LSM_ACC_SET_ODR = {12.5:0b00110111, # 12.5Hz
                   25 : 0b01000111, # 25Hz
                   50 : 0b01010111} # 50Hz

LSM_MAG_SET_ODR = {12.5:0b01101000, # 12.5Hz
                   25 : 0b01101100, # 25Hz
                   50 : 0b01110000} # 50Hz

# Scale
LSM_ACC_SET_SCALE = {2: 0b00000000, #+/- 2g
                     4: 0b00001000, #+/- 4g
                     6: 0b00010000, #+/- 6g
                     8: 0b00011000, #+/- 8g
					 16:0b00100000} #+/- 16g

LSM_MAG_SET_SCALE = {2: 0b00000000, # +/- 2 gauss
                     4: 0b00100000, # +/- 4 gauss
                     8: 0b01000000, # +/- 8 gauss
                     12:0b01100000} # +/- 12 gauss

# Sensitivity
# raw value * sensitivity = value
LSM_ACC_SENS = {2: 0.061e-3, # g/LSB # for 2g scale
                4: 0.122e-3, # g/LSB # for 4g scale
                6: 0.183e-3, # g/LSB # etc
                8: 0.244e-3, # g/LSB
                16:0.732e-3} # g/LSB

LSM_MAG_SENS = {2: 0.080e-3, # gauss/LSB # for 2gauss scale
                4: 0.160e-3, # gauss/LSB # for 4gauss scale
                6: 0.320e-3, # gauss/LSB # etc
                12:0.479e-3} # gauss/LSB

########################################################################
## Accelerometer Class ##
#########################
class Accelerometer:
	def __init__(self, bus, acc_odr=50, acc_scale=2, mag_odr=50, mag_scale=4):
		self.bus = bus
		self.acc_odr = acc_odr
		self.acc_scale = acc_scale
		self.mag_odr = mag_odr
		self.mag_scale = mag_scale
		self.acc_sens = LSM_ACC_SENS[acc_scale]
		self.mag_sens = LSM_MAG_SENS[mag_scale]

		if self.bus.read_byte_data(LSM, LSM_WHOAMI_ADDRESS) != LSM_WHOAMI_CONTENTS:
			raise Exception("LSM not found at address {}.".format(LSM))
		else:
			# Enable accelerometer axes and set ODR (output data rate) = 50 Hz
			self.bus.write_byte_data(LSM, LSM_CTRL_1, LSM_ACC_SET_ODR[self.acc_odr])
			# Set acceleration full-scale to +/-2g
			self.bus.write_byte_data(LSM, LSM_CTRL_2, LSM_ACC_SET_SCALE[self.acc_scale])
			# Disable thermometer, set magnetic resolution high, ODR 50Hz
			self.bus.write_byte_data(LSM, LSM_CTRL_5, LSM_MAG_SET_ODR[self.mag_odr])
			# Set magnetic full-scale to +/- 4 gauss
			self.bus.write_byte_data(LSM, LSM_CTRL_6, LSM_MAG_SET_SCALE[self.mag_scale])
			# Set magnetometer low power mode off
			self.bus.write_byte_data(LSM, LSM_CTRL_7, 0b00000000)
			print("Accelerometer/magnetometer set up.")

	def read_acc(self):
		x_L = self.bus.read_byte_data(LSM, LSM_ACC_X_L)
		x_H = self.bus.read_byte_data(LSM, LSM_ACC_X_H)
		y_L = self.bus.read_byte_data(LSM, LSM_ACC_Y_L)
		y_H = self.bus.read_byte_data(LSM, LSM_ACC_Y_H)
		z_L = self.bus.read_byte_data(LSM, LSM_ACC_Z_L)
		z_H = self.bus.read_byte_data(LSM, LSM_ACC_Z_H)
		self.accx = (x_H << 8 | x_L) * self.acc_sens
		self.accy = (y_H << 8 | y_L) * self.acc_sens
		self.accz = (z_H << 8 | z_L) * self.acc_sens
		return (self.accx, self.accy, self.accz)

	def read_mag(self):
		x_L = self.bus.read_byte_data(LSM, LSM_MAG_X_L)
		x_H = self.bus.read_byte_data(LSM, LSM_MAG_X_H)
		y_L = self.bus.read_byte_data(LSM, LSM_MAG_Y_L)
		y_H = self.bus.read_byte_data(LSM, LSM_MAG_Y_H)
		z_L = self.bus.read_byte_data(LSM, LSM_MAG_Z_L)
		z_H = self.bus.read_byte_data(LSM, LSM_MAG_Z_H)
		self.magx = (x_H << 8 | x_L) * self.mag_sens
		self.magy = (y_H << 8 | y_L) * self.mag_sens
		self.magz = (z_H << 8 | z_L) * self.mag_sens
		return (self.magx, self.magy, self.magz)

########################################################################
## Main ##
##########
if __name__ == "__main__":
	from smbus import SMBus
	from time import sleep

	# Initialise the i2c bus
	I2CBUS_NUMBER = 1
	bus = SMBus(I2CBUS_NUMBER)

	# Initialise the accelerometer
	accelerometer1 = Accelerometer(bus)

	try:
		while True:
			print(accelerometer1.read_acc())
			print(accelerometer1.read_mag())
			print("")
			#sleep(1/50)
			sleep(1/3)
	except KeyboardInterrupt:
		print("Exiting...")

