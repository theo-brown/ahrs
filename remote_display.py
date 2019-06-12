from pyqtgraph.Qt import QtGui, QtCore
import plot as plt
import pyqtgraph as pg
import sys
import time
import communications as com


class ConnectionHandler(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected = False
        self.client = com.ClientSocket()

    @QtCore.pyqtSlot(str, int)
    def connect(self, address, port):
        if not self.connected:
            self.client.server_address = address
            self.client.server_port = port
            self.client.connect()
            self.connected = True

    @QtCore.pyqtSlot()
    def disconnect(self):
        if self.connected:
            self.client.disconnect()
            self.connected = False


class DataReceiver(QtCore.QObject):
    
    start_signal = QtCore.pyqtSignal()    
    
    def __init__(self, parent, connection_handler, accelerometer_data_items, magnetometer_data_items, gyroscope_data_items, barometer_data_item):
        super().__init__(parent)
        self.connection_handler = connection_handler
        self.accelerometer_data_items = accelerometer_data_items
        self.magnetometer_data_items = magnetometer_data_items
        self.gyroscope_data_items = gyroscope_data_items
        self.barometer_data_item = barometer_data_item

    @QtCore.pyqtSlot()
    def receive_data(self):
        print("Starting the 'receive data' loop")
        time_zero = time.time()
        while True:
            if self.connection_handler.connected:
                packets = self.connection_handler.client.read()
                for packet in packets:
                    if packet:
                        print(packet)
                        packet_length, data_source, data = packet
                        timestamp = time.time() - time_zero
                        if data_source == com.ACCELEROMETER_ID:
                            self.accelerometer_data_items['x'].update_data(timestamp, data[0])
                            self.accelerometer_data_items['y'].update_data(timestamp, data[1])
                            self.accelerometer_data_items['z'].update_data(timestamp, data[2])
                        elif data_source == com.MAGNETOMETER_ID:
                            self.magnetometer_data_items['x'].update_data(timestamp, data[0])
                            self.magnetometer_data_items['y'].update_data(timestamp, data[1])
                            self.magnetometer_data_items['z'].update_data(timestamp, data[2])                       
                        elif data_source == com.GYROSCOPE_ID:
                            self.gyroscope_data_items['x'].update_data(timestamp, data[0])
                            self.gyroscope_data_items['y'].update_data(timestamp, data[1])
                            self.gyroscope_data_items['z'].update_data(timestamp, data[2])
                        elif data_source == com.BAROMETER_ID:
                            self.barometer_data_item.update_data(timestamp, data[0])


class RemoteDisplayWindow(QtGui.QMainWindow):
    connect_signal = QtCore.pyqtSignal(str, int)        
    disconnect_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Address label
        self.address_label = QtGui.QLabel("Server:")
        self.address_label.setAlignment(QtCore.Qt.AlignRight |
                                       QtCore.Qt.AlignVCenter)
        
        # Address bar
        self.address_bar = QtGui.QLineEdit()
        # Create a regex for the IP address
        ip_values = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QtCore.QRegExp("^" + ip_values + "\\." + ip_values + "\\."
                                  + ip_values + "\\." + ip_values + "$")
        self.address_bar.setValidator(QtGui.QRegExpValidator(ip_regex, self))
        self.address_bar.setText("192.168.42.1")
        
        # Port bar
        self.port_bar = QtGui.QLineEdit()
        self.port_bar.setValidator(QtGui.QIntValidator())
        self.port_bar.setText("12345")

        # Connect button
        self.connect_button = QtGui.QPushButton("&Connect")
        self.connect_button.clicked.connect(self.toggle_connect)
        self.connected = False

        # Accelerometer plot
        self.accelerometer_plotwidget = pg.PlotWidget(title='Accelerometer')

        self.accelerometer_plotwidget.plot()
        self.accelerometer_plotwidget.enableAutoRange()
        self.accelerometer_plotwidget.showGrid(x=True, y=True)
        self.accelerometer_data_items = {'x': plt.UpdatingDataItem(),
                                         'y': plt.UpdatingDataItem(),
                                         'z': plt.UpdatingDataItem()}
        for key, item in self.accelerometer_data_items.items():
            self.accelerometer_plotwidget.addItem(item)
        self.accelerometer_data_items['x'].setPen('r')
        self.accelerometer_data_items['y'].setPen('g')
        self.accelerometer_data_items['z'].setPen('b')
        
        # Magnetometer plot
        self.magnetometer_plotwidget = pg.PlotWidget(title='Magnetometer')

        self.magnetometer_plotwidget.plot()
        self.magnetometer_plotwidget.enableAutoRange()
        self.magnetometer_plotwidget.showGrid(x=True, y=True)
        self.magnetometer_data_items = {'x': plt.UpdatingDataItem(),
                                        'y': plt.UpdatingDataItem(),
                                        'z': plt.UpdatingDataItem()}
        for key, item in self.magnetometer_data_items.items():
            self.magnetometer_plotwidget.addItem(item)
        self.magnetometer_data_items['x'].setPen('r')
        self.magnetometer_data_items['y'].setPen('g')
        self.magnetometer_data_items['z'].setPen('b')


        # Gyroscope plot
        self.gyroscope_plotwidget = pg.PlotWidget(title='Gyroscope')

        self.gyroscope_plotwidget.plot()
        self.gyroscope_plotwidget.enableAutoRange()
        self.gyroscope_plotwidget.showGrid(x=True, y=True)
        self.gyroscope_data_items = {'x': plt.UpdatingDataItem(),
                                     'y': plt.UpdatingDataItem(),
                                     'z': plt.UpdatingDataItem()}
        for key, item in self.gyroscope_data_items.items():
            self.gyroscope_plotwidget.addItem(item)
        self.gyroscope_data_items['x'].setPen('r')
        self.gyroscope_data_items['y'].setPen('g')
        self.gyroscope_data_items['z'].setPen('b')


        # Barometer plot
        self.barometer_plotwidget = pg.PlotWidget(title='Barometer')

        self.barometer_plotwidget.plot()
        self.barometer_plotwidget.enableAutoRange()
        self.barometer_plotwidget.showGrid(x=True, y=True)
        self.barometer_data_item = plt.UpdatingDataItem()
        self.barometer_plotwidget.addItem(self.barometer_data_item)

        # Orientation plots
#        self.orientation_plots = {'xy': pg.PlotWidget(title='XY',
#                                                      labels={'left': 'Y',
#                                                              'bottom': 'X'}),
#                                  'yz': pg.PlotWidget(title='YZ',
#                                                      labels={'left': 'Z',
#                                                              'bottom': 'Y'}),
#                                  'zx': pg.PlotWidget(title='ZX',
#                                                      labels={'left': 'Z',
#                                                              'bottom': 'X'})}
#        self.orientation_data = {}
#        column = 0
#        for key, widget in self.orientation_plots.items():
#            self.grid.addWidget(widget, 3, column)
#            column += 1
#            widget.plot()
#            widget.showGrid(x=True, y=True)
#            widget.setLimits(xMin=-1, xMax=1, yMin=-1, yMax=1,
#                             minXRange=2, maxXRange=2,
#                             minYRange=2, maxYRange=2)
#            widget.getAxis('left').setStyle(showValues=False)
#            widget.getAxis('bottom').setStyle(showValues=False)
#            self.orientation_data[key] = plt.UpdatingDataItem(symbol='o')
#            widget.addItem(self.orientation_data[key])

        # Connection handler thread
        # Create the connection handler object
        self.connection_handler = ConnectionHandler()
        # Create a thread for it
        self.connection_handler_thread = QtCore.QThread()
        self.connection_handler.moveToThread(self.connection_handler_thread)
        # Connect some asynchronous slots
        self.connect_signal.connect(self.connection_handler.connect)
        self.disconnect_signal.connect(self.connection_handler.disconnect) 
        # Start the thread
        self.connection_handler_thread.start()
       
        # Data receiving thread
        # Create the connection handler object
        self.data_receiver = DataReceiver(None, self.connection_handler,  self.accelerometer_data_items, self.magnetometer_data_items, self.gyroscope_data_items, self.barometer_data_item)
        # Create a thread for it
        self.data_receiver_thread = QtCore.QThread()
        self.data_receiver.moveToThread(self.data_receiver_thread)
        self.data_receiver_thread.started.connect(self.data_receiver.receive_data)
        # Start the thread        
        self.data_receiver_thread.start()
        
        # GUI:
        #        0        1        2        3        4       5
        #   |-----------------------------------------------------|
        # 0 |        |        | Label  | Address|  Port  | Connect|
        #   |-----------------------------------------------------|
        # 1 |      Accelerometer       |         Gyroscope        |
        #   |-----------------------------------------------------|
        # 2 |       Magnetometer       |         Barometer        |
        #   |-----------------------------------------------------|
        # 3 |   XY   |   YZ   |   ZX   |        |        |        | 
        #   |-----------------------------------------------------|
        self.setWindowTitle('Remote Display')
        self.resize(650, 800)

        self.main_widget = QtGui.QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.grid = QtGui.QGridLayout()
        self.grid.setRowMinimumHeight(0, 50)
        self.grid.setRowMinimumHeight(1, 200)
        self.grid.setRowMinimumHeight(2, 200)
        #self.grid.setRowMinimumHeight(3, 200)
        self.grid.setColumnMinimumWidth(0, 200)
        self.grid.setColumnMinimumWidth(1, 200)
        self.grid.setColumnMinimumWidth(2, 200)
        self.grid.setColumnMinimumWidth(3, 200)
        self.grid.setColumnMinimumWidth(4, 200)
        self.grid.setColumnMinimumWidth(5, 200)
        self.grid.setSpacing(10)
        self.main_widget.setLayout(self.grid)
        
        self.grid.addWidget(self.address_label, 0, 2)
        self.grid.addWidget(self.address_bar, 0, 3)
        self.grid.addWidget(self.port_bar, 0, 4)
        self.grid.addWidget(self.connect_button, 0, 5)
        self.grid.addWidget(self.accelerometer_plotwidget, 1, 0, 1, 3)
        self.grid.addWidget(self.magnetometer_plotwidget, 2, 0, 1, 3)
        self.grid.addWidget(self.gyroscope_plotwidget, 1, 3, 1, 3)
        self.grid.addWidget(self.barometer_plotwidget, 2, 3, 1, 3)


    def toggle_connect(self):
        if self.connection_handler.connected:
            self.disconnect_signal.emit()
            self.connect_button.setText("&Connect")
            self.address_bar.setEnabled(True)
            self.port_bar.setEnabled(True)
        else:
            address = self.address_bar.text()
            port = int(self.port_bar.text())
            self.connect_signal.emit(address, port)
            self.connect_button.setText("Dis&connect")
            self.address_bar.setEnabled(False)
            self.port_bar.setEnabled(False)

if __name__ == '__main__':
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    window = RemoteDisplayWindow()
    window.show()
    sys.exit(app.exec_())
