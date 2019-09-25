import sys
import time
from pyqtgraph.Qt import QtGui, QtCore
import plot as plt
import communications as com
from kalman_filter import KalmanFilter


###############################################################################
## Master application object ##
###############################
class RemoteDisplayApplication(QtGui.QApplication):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.aboutToQuit.connect(self.deleteLater)

        self.main_window = MainWindow()
        self.main_window.show()

        self._init_connection_handler()
        self._init_data_receiver()

        #self.exec_()
    
    def _init_connection_handler(self):
        # Create the connection handler object
        self.connection_handler = ConnectionHandler()
        # Create a thread for it
        self.connection_handler_thread = QtCore.QThread()
        self.connection_handler.moveToThread(self.connection_handler_thread)
        # Connect slots
        self.main_window.connect_signal.connect(self.connection_handler.connect)
        self.main_window.disconnect_signal.connect(self.connection_handler.disconnect)
        self.aboutToQuit.connect(self.connection_handler_thread.quit)
        # Start the thread
        self.connection_handler_thread.start()
    
    def _init_data_receiver(self):
        # Create the connection handler object
        self.data_receiver = DataReceiver(None, self.connection_handler)
        # Create a thread for it
        self.data_receiver_thread = QtCore.QThread()
        self.data_receiver.moveToThread(self.data_receiver_thread)
        # Connect slots
        self.data_receiver.data_received_signal.connect(self.main_window.data_received)
        self.data_receiver_thread.started.connect(self.data_receiver.receive_data)
        self.aboutToQuit.connect(self.data_receiver_thread.quit)
        # Start the thread
        self.data_receiver_thread.start()


###############################################################################
## Main window object ##
########################
class MainWindow(QtGui.QMainWindow):

    # Signals:
    connect_signal = QtCore.pyqtSignal(str, int)
    disconnect_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self._initialise_gui_widgets()
        self._setup_gui()

        self.connected = False
        self.time_zero = time.time()

    def _initialise_gui_widgets(self):
        """
        Create all the widgets for the window.
        """
        # # Main widget
        self.main_widget = QtGui.QWidget()

        # # Address label
        self.address_label = QtGui.QLabel("Server:")
        self.address_label.setAlignment(QtCore.Qt.AlignRight |
                                        QtCore.Qt.AlignVCenter)

        # # Address bar
        self.address_bar = QtGui.QLineEdit()

        # Create a regex validator for the IP address
        ip_values = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QtCore.QRegExp("^" + ip_values + "\\." +
                                  ip_values + "\\." + ip_values +
                                  "\\." + ip_values + "$")
        ip_validator = QtGui.QRegExpValidator(ip_regex, self)

        self.address_bar.setValidator(ip_validator)
        self.address_bar.setText("192.168.42.1")

        # # Port bar
        self.port_bar = QtGui.QLineEdit()
        self.port_bar.setValidator(QtGui.QIntValidator())
        self.port_bar.setText("12345")

        # # Connect button
        self.connect_button = QtGui.QPushButton("&Connect")
        self.connect_button.clicked.connect(self._toggle_connect)

        # # Plot widgets
        self.plot_widgets = {'accelerometer': plt.UpdatingPlotWidget(title='Accelerometer'),
                             'magnetometer': plt.UpdatingPlotWidget(title='Magnetometer'),
                             'gyroscope': plt.UpdatingPlotWidget(title='Gyroscope'),
                             'barometer': plt.UpdatingPlotWidget(title='Barometer')}

        for name, widget in self.plot_widgets.items():
            if name == 'barometer':
                widget.add_item('altitude', pen='k')
                widget.add_item('filtered', pen='r')
                self.filter1 = KalmanFilter(x_prior=0, P_prior=2, A=1, B=0, H=1, Q=0.005, R=1.02958)
            else:
                widget.add_item('x', pen='r')
                widget.add_item('y', pen='g')
                widget.add_item('z', pen='b')

    def _setup_gui(self):
        """
        Add all the widgets to the window.

        Layout:
                0        1        2        3        4       5
           |-----------------------------------------------------|
         0 |        |        | Label  | Address | Port | Connect |
           |-----------------------------------------------------|
         1 |      Accelerometer       |         Gyroscope        |
           |-----------------------------------------------------|
         2 |       Magnetometer       |         Barometer        |
           |-----------------------------------------------------|
         3 |   XY   |   YZ   |   ZX   |         |      |         |
           |-----------------------------------------------------|
        """
        # # Window setup
        self.setWindowTitle('Remote Display')
        self.resize(450, 800)

        # # Main widget setup
        self.main_widget = QtGui.QWidget()
        self.setCentralWidget(self.main_widget)

        # # Layout setup
        self.grid = QtGui.QGridLayout()
        self.main_widget.setLayout(self.grid)

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

        # # Add widgets to layout
        self.grid.addWidget(self.address_label, 0, 2)
        self.grid.addWidget(self.address_bar, 0, 3)
        self.grid.addWidget(self.port_bar, 0, 4)
        self.grid.addWidget(self.connect_button, 0, 5)
        plot_locations = [(1, 0), (1, 3), (2, 0), (2, 3)]

        i = 0
        for name, widget in self.plot_widgets.items():
            self.grid.addWidget(widget,
                                plot_locations[i][0], plot_locations[i][1],
                                1, 3)
            i += 1

    @QtCore.pyqtSlot()
    def _toggle_connect(self):
        """
        Slot for when connect button is clicked
        """
        if self.connected:
            self.disconnect_signal.emit()
            self.connect_button.setText("&Connect")
            self.address_bar.setEnabled(True)
            self.port_bar.setEnabled(True)
            self.connected = False
        else:
            address = self.address_bar.text()
            port = int(self.port_bar.text())
            self.connect_signal.emit(address, port)
            self.connect_button.setText("Dis&connect")
            self.address_bar.setEnabled(False)
            self.port_bar.setEnabled(False)
            self.connected = True

    @QtCore.pyqtSlot(list)
    def data_received(self, received_data):
        """
        Slot for when data is received - updates the plots
        """
        data_source = received_data[0]
        values = received_data[1]
        t = time.time() - self.time_zero
        if data_source == com.BAROMETER_ID:
            self.plot_widgets['barometer'].get_item('altitude').update_data(t, values[0])
            self.plot_widgets['barometer'].get_item('filtered').update_data(t, self.filter1.update(u_input=0, z_measurement=values[0])[0])
        elif data_source == com.ACCELEROMETER_ID:
            if len(values) < 3:
                print("Error: Expected 3 values for accelerometer data, got {}".format(len(values)))
            else:
                self.plot_widgets['accelerometer'].get_item('x').update_data(t, values[0])
                self.plot_widgets['accelerometer'].get_item('y').update_data(t, values[1])
                self.plot_widgets['accelerometer'].get_item('z').update_data(t, values[2])
        elif data_source == com.MAGNETOMETER_ID:
            if len(values) < 3:
                print("Error: Expected 3 values for magnetometer data, got {}".format(len(values)))
            else:
                self.plot_widgets['magnetometer'].get_item('x').update_data(t, values[0])
                self.plot_widgets['magnetometer'].get_item('y').update_data(t, values[1])
                self.plot_widgets['magnetometer'].get_item('z').update_data(t, values[2])
        elif data_source == com.GYROSCOPE_ID:
            if len(values) < 3:
                print("Error: Expected 3 values for gyroscope data, got {}".format(len(values)))
            else:
                self.plot_widgets['gyroscope'].get_item('x').update_data(t, values[0])
                self.plot_widgets['gyroscope'].get_item('y').update_data(t, values[1])
                self.plot_widgets['gyroscope'].get_item('z').update_data(t, values[2])


###############################################################################
## Connection handler ##
########################
class ConnectionHandler(QtCore.QObject):
    
    # Signals
    connected_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected = False
        self.mutex = QtCore.QMutex()
        self.client = com.ClientSocket()

    @QtCore.pyqtSlot(str, int)
    def connect(self, address, port):
        self.mutex.lock()
        if not self.connected:
            self.client.server_address = address
            self.client.server_port = port
            self.client.connect()
            self.connected = True
        self.mutex.unlock()

    @QtCore.pyqtSlot()
    def disconnect(self):
        self.mutex.lock()
        if self.connected:
            self.client.disconnect()
            self.connected = False
        self.mutex.unlock()


###############################################################################
## Data receiver ##
###################
class DataReceiver(QtCore.QObject):

    # Signals
    data_received_signal = QtCore.pyqtSignal(list)  # [data_source, data]

    def __init__(self, parent, connection_handler):
        super().__init__(parent)
        self.connection_handler = connection_handler

    @QtCore.pyqtSlot()
    def receive_data(self):
        while True:
            self.connection_handler.mutex.lock()
            if self.connection_handler.connected:
                   packets = self.connection_handler.client.read()
                   for packet in packets:
                       if packet:
                           packet_length, data_source, data = packet
                           self.data_received_signal.emit([data_source, data])
            self.connection_handler.mutex.unlock()

###############################################################################
## Main ##
##########
if __name__ == "__main__":
    app = RemoteDisplayApplication(sys.argv)
    app.exec_()
        