from gps3.agps3threaded import AGPS3mechanism as GPSSensor

# Modify the GPSSensor class to make it look tidier
# For example, enable us to access the lat property using gps1.lat rather than
# gps1.data_stream.lat
GPSSensor.mode = property(lambda self: self.data_stream.mode) # 0 = none seen, 1 = no fix, 2 = 2D, 3= 3D

GPSSensor.lat = property(lambda self: self.data_stream.lat) # Lat in degrees +/- = N/S
GPSSensor.epy = property(lambda self: self.data_stream.epy) # Error in lat (m)

GPSSensor.lon = property(lambda self: self.data_stream.lon) # Lon in degrees +/- = E/W
GPSSensor.epx = property(lambda self: self.data_stream.epx) # Error in Lon (m)

GPSSensor.alt = property(lambda self: self.data_stream.alt) # Altitude in m
GPSSensor.epv = property(lambda self: self.data_stream.epv) # Error in altitude (m)

GPSSensor.magtrack = property(lambda self: self.data_stream.magtrack) # Course over ground, degrees magnetic
GPSSensor.epd = property(lambda self: self.data_stream.epd) # Course error in degrees

GPSSensor.speed = property(lambda self: self.data_stream.speed) # Speed over ground in m/s
GPSSensor.eps = property(lambda self: self.data_stream.eps) # Speed error in m/s

GPSSensor.climb = property(lambda self: self.data_stream.climb) # Climb rate in m/s
GPSSensor.epc = property(lambda self: self.data_stream.epc) # Climb error in m/s

# Create functions that will be used as methods of GPSSensor objects
def initialise(self):
    self.stream_data()
    self.run_thread()

# Assign functions as methods of GPSSensor
GPSSensor.initialise = initialise
    
if __name__ == '__main__':
    
    from time import sleep
    
    gps1 = GPSSensor()
    gps1.initialise()

    try:
        while gps1.mode != 1 and gps1.mode != 0:
            print(gps1.lat, gps1.lon)
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
