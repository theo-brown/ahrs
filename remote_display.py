from pyqtgraph.Qt import QtGui, QtCore
import plot as plt
import pyqtgraph as pg
import sys
import time
import communications as com


class Main(QtCore.QObject):
    def __init__(self, parent=None,
                 accelerometer_data_items=None,
                 magnetometer_data_items=None,
                 gyroscope_data_items=None,
                 barometer_data_item=None):
        super().__init__(parent)
        self.accelerometer_data_items = accelerometer_data_items
        self.magnetometer_data_items = magnetometer_data_items
        self.gyroscope_data_items = gyroscope_data_items
        self.barometer_data_item = barometer_data_item

    @QtCore.pyqtSlot()
    def execute(self):
        time_zero = time.time()

        self.client = com.ClientSocket()
        self.client.connect()

        while True:
            packets = self.client.read()
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


class RemoteDisplayApplication(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(RemoteDisplayApplication, self).__init__(parent)

        self.setWindowTitle('Remote Display')
        self.resize(650, 800)

        self.main_widget = QtGui.QWidget()
        self.setCentralWidget(self.main_widget)
        
        #        0        1        2        3        4       5
        #   |-----------------------------------------------------|
        # 0 |        |        |        |        |        | Connect|
        #   |-----------------------------------------------------|
        # 1 |      Accelerometer       |         Gyroscope        |
        #   |-----------------------------------------------------|
        # 2 |       Magnetometer       |         Barometer        |
        #   |-----------------------------------------------------|
        # 3 |   XY   |   YZ   |   ZX   |        |        |        | 
        #   |-----------------------------------------------------|
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

        # Connect button
        self.connect_button = QtGui.QPushButton("&Connect")
        self.grid.addWidget(self.connect_button, 0, 5)

        # Accelerometer plot
        self.accelerometer_plotwidget = pg.PlotWidget(title='Accelerometer')
        self.grid.addWidget(self.accelerometer_plotwidget, 1, 0, 1, 3)

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
        self.grid.addWidget(self.magnetometer_plotwidget, 2, 0, 1, 3)

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
        self.grid.addWidget(self.gyroscope_plotwidget, 1, 3, 1, 3)

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
        self.grid.addWidget(self.barometer_plotwidget, 2, 3, 1, 3)

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

        # Main thread
        self.main = Main(accelerometer_data_items=self.accelerometer_data_items,
                         magnetometer_data_items=self.magnetometer_data_items,
                         gyroscope_data_items=self.gyroscope_data_items,
                         barometer_data_item=self.barometer_data_item)
        self.main_thread = QtCore.QThread()
        self.main.moveToThread(self.main_thread)
        self.main_thread.start()
        self.connect_button.clicked.connect(self.main.execute)        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = RemoteDisplayApplication()
    window.show()
    app.exec_()
