import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('antialias', True)
DEFAULT_LINE_WIDTH = 1
DEFAULT_LINE_COLOUR = 'k'
DEFAULT_SPOT_COLOUR = 'k'
DEFAULT_SPOT_SIZE = 10
DEFAULT_PEN = pg.mkPen(DEFAULT_LINE_COLOUR, width=DEFAULT_LINE_WIDTH)
DEFAULT_BRUSH = pg.mkBrush(DEFAULT_SPOT_COLOUR)

class UpdatingDataItem(pg.PlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSymbolPen(None)
        self.setSymbolBrush(DEFAULT_BRUSH)
        self.setSymbolSize(DEFAULT_SPOT_SIZE)
        if self.opts['symbol'] is not None:
            # Disable line if it's a scatter plot
            self.setPen(None)
        else:
            self.setPen(DEFAULT_PEN)

    def update_data(self, new_x, new_y):
        if new_x.size != new_y.size:
            raise Exception("xData and yData must be the same size")
        x, y = self.getData()
        # Move the data to the left
        num_new_datapoints = new_x.size
        x = np.roll(x, -num_new_datapoints)
        y = np.roll(y, -num_new_datapoints)
        # Add the most recent data to the end of the array
        x[-num_new_datapoints:] = new_x
        y[-num_new_datapoints:] = new_y
        # Update the curve
        self.setData(x, y)


if __name__ == '__main__':
    import sys

    N = 300
    y = np.random.normal(size=N)
    x = np.arange(N)
    a = np.random.normal(size=N)
    b = np.random.normal(size=N)

    window = pg.GraphicsWindow()
    window.setWindowTitle('Scrolling Plots')

    plot1 = window.addPlot()
    plot1.showGrid(x=True, y=True)
    dataitem = UpdatingDataItem(x, y)
    plot1.addItem(dataitem)

    def update_plot1():
        new_y = np.asarray(np.random.normal())
        new_x = np.asarray(dataitem.xData[-1] + 1)
        dataitem.update_data(new_x, new_y)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update_plot1)
    timer.start(50)

    plot2 = window.addPlot()
    plot2.showGrid(x=True, y=True)
    scatteritem = UpdatingDataItem(a, b, symbol='o')
    plot2.addItem(scatteritem)

    def update_plot2():
        new_a = np.asarray(np.random.normal())
        new_b = np.asarray(np.random.normal())
        scatteritem.update_data(new_a, new_b)

    timer2 = pg.QtCore.QTimer()
    timer2.timeout.connect(update_plot2)
    timer2.start(50)


    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
