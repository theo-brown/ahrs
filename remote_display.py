from pyqtgraph.Qt import QtGui, QtCore
import plot as plt
import pyqtgraph as pg
import sys
import time
import communications as com
import numpy as np


class Main(QtCore.QObject):
    def __init__(self, parent=None, data_items=None):
        super().__init__(parent)
        self.data_items = data_items

    @QtCore.pyqtSlot()
    def execute(self):
        time_zero = time.time()

        self.client = com.ClientSocket()
        self.client.connect()

        while True:
            packets = self.client.read()
            for packet in packets:
                if packet:
                    packet_length, data_source, data = packet
                    timestamp = time.time() - time_zero
                    self.data_items['x'].update_data(timestamp, data[0])
                    self.data_items['y'].update_data(timestamp, data[1])
                    self.data_items['z'].update_data(timestamp, data[2])


class RemoteDisplayApplication(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(RemoteDisplayApplication, self).__init__(parent)

        self.setWindowTitle('Remote Display')
        self.resize(900, 650)

        self.main_widget = QtGui.QWidget()
        self.setCentralWidget(self.main_widget)

        self.grid = QtGui.QGridLayout()
        self.grid.setRowMinimumHeight(0, 50)
        self.grid.setRowMinimumHeight(1, 300)
        self.grid.setRowMinimumHeight(2, 300)
        self.grid.setColumnMinimumWidth(0, 300)
        self.grid.setColumnMinimumWidth(1, 300)
        self.grid.setColumnMinimumWidth(2, 300)
        self.grid.setSpacing(10)
        self.main_widget.setLayout(self.grid)

        # Connect button
        self.connect_button = QtGui.QPushButton("&Connect")
        self.grid.addWidget(self.connect_button, 0, 2)

        # Logging plot
        self.logging_plotwidget = pg.PlotWidget()
        self.grid.addWidget(self.logging_plotwidget, 1, 0, 1, 3)

        self.logging_plotwidget.plot()
        self.logging_plotwidget.enableAutoRange()
        self.logging_plotwidget.showGrid(x=True, y=True)
        self.logging_data_items = {'x': plt.UpdatingDataItem(),
                                   'y': plt.UpdatingDataItem(),
                                   'z': plt.UpdatingDataItem()}
        for key, item in self.logging_data_items.items():
            self.logging_plotwidget.addItem(item)
        self.logging_data_items['x'].setPen('r')
        self.logging_data_items['y'].setPen('g')
        self.logging_data_items['z'].setPen('b')

        # Orientation plots
        self.orientation_plots = {'xy': pg.PlotWidget(title='XY',
                                                      labels={'left': 'Y',
                                                              'bottom': 'X'}),
                                  'yz': pg.PlotWidget(title='YZ',
                                                      labels={'left': 'Z',
                                                              'bottom': 'Y'}),
                                  'zx': pg.PlotWidget(title='ZX',
                                                      labels={'left': 'Z',
                                                              'bottom': 'X'})}
        self.orientation_data = {}
        column = 0
        for key, widget in self.orientation_plots.items():
            self.grid.addWidget(widget, 2, column)
            column += 1
            widget.plot()
            widget.showGrid(x=True, y=True)
            widget.setLimits(xMin=-1, xMax=1, yMin=-1, yMax=1,
                             minXRange=2, maxXRange=2,
                             minYRange=2, maxYRange=2)
            widget.getAxis('left').setStyle(showValues=False)
            widget.getAxis('bottom').setStyle(showValues=False)
            self.orientation_data[key] = plt.UpdatingDataItem(symbol='o')
            widget.addItem(self.orientation_data[key])

        # Main thread
        self.main = Main(data_items=self.logging_data_items)
        self.main_thread = QtCore.QThread()
        self.main.moveToThread(self.main_thread)
        self.main_thread.start()
        self.connect_button.clicked.connect(self.main.execute)        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = RemoteDisplayApplication()
    window.show()
    app.exec_()
