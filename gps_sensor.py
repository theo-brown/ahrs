########################################################################
## Imports ##
#############
import gps
from threading import Thread

########################################################################
## GPS Sensor Class ##
######################
class GPSSensorThread(Thread):
	def __init__(self):
		# Initialise the thread
		Thread.__init__(self)
		# Initialise the link to GPSD
		self.gpsd = gps.gps(mode=gps.WATCH_ENABLE)
		# Define a variable to show the state
		self.running = False
	
	def run(self):
		# This function is run when the thread is started using self.start()
		# It's not meant to be run manually
		# Start the data stream
		self.running = True
		while self.running:
			# Collect each next report as it comes in to clear the buffer
			self.gpsd.next()
	
	def stop(self):
		# Stop clearing the buffer and join the thread
		self.running = False
		print("Joining GPSSensorThread...")
		self.join()
		print("Done.")

	@property
	def mode(self):
		# 0=no mode value yet seen, 1=no fix, 2=2D, 3=3D
		return self.gpsd.fix.mode
	
	@property
	def time(self):
		# Time/date stamp
		return self.gpsd.fix.time
	
	@property
	def ept(self):
		# Estimated timestamp error
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.ept
	
	@property
	def latitude(self):
		# Lat in degrees +/- is N/S
		return self.gpsd.fix.latitude
	
	@property
	def epy(self):
		# Estimated Lat error in metres
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.epy
	
	@property
	def longitude(self):
		# Long in degrees +/- is E/W
		return self.gpsd.fix.longitude
	
	@property
	def epx(self):
		# Estimated long error in metres
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.epx
	
	@property
	def altitude(self):
		# Altitude in metres
		return self.gpsd.fix.altitude
	
	@property
	def epv(self):
		# Estimated vertical error in metres
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.epv
	
	@property
	def track(self):
		# Course over ground, degrees (TODO: Is this from true north or magnetic?)
		return self.gpsd.fix.track
	
	@property
	def epd(self):
		# Estimated direction error in degrees
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.epd
		
	@property
	def speed(self):
		# Speed over ground in m/s
		return self.gpsd.fix.speed
	
	@property
	def eps(self):
		# Estimated speed error in m/s
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.eps
	
	@property
	def climb(self):
		# Climb (+) or sink (-) rate in m/s
		return self.gpsd.fix.climb

	@property
	def epc(self):
		# Estimated climb/sink error in m/s
		# All estimated errors are 95% confidence interval
		return self.gpsd.fix.epc


if __name__ == '__main__':
	from time import sleep
	
	# Initialise the gps
	gps1 = GPSSensorThread()
	gps1.start()
	
	try:
		while True:
			print(gps1.mode, # 0=no mode value yet seen, 1=no fix, 2=2D, 3=3D
				  gps1.time, # Time/date stamp
				  gps1.ept, # Estimated timestamp error
				  gps1.latitude, # Lat in degrees +/- is N/S
				  gps1.epy, # Estimated Lat error in metres
				  gps1.longitude, # Long in degrees +/- is E/W
				  gps1.epx, # Estimated long error in metres
				  gps1.altitude, # Altitude in metres
				  gps1.epv, # Estimated vertical error in metres
				  gps1.track, # Course over ground, degrees (TODO: Is this from true north or magnetic?)
 				  gps1.epd, # Estimated direction error in degrees
				  gps1.speed, # Speed over ground in m/s
				  gps1.eps, # Estimated speed error in m/s
				  gps1.climb, # Climb (+) or sink (-) rate in m/s
				  gps1.epc) # Estimated climb/sink error in m/s
			sleep(1)
	except KeyboardInterrupt:
		print("Exiting...")
	finally:
		gps1.stop()
