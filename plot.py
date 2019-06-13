import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

###############################################################################
## PyQtGraph configuration ##
#############################
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('antialias', True)
DEFAULT_LINE_WIDTH = 1
DEFAULT_LINE_COLOUR = 'k'
DEFAULT_SPOT_COLOUR = 'k'
DEFAULT_SPOT_SIZE = 10
DEFAULT_PEN = pg.mkPen(DEFAULT_LINE_COLOUR, width=DEFAULT_LINE_WIDTH)
DEFAULT_BRUSH = pg.mkBrush(DEFAULT_SPOT_COLOUR)


###############################################################################
class UpdatingDataItem(pg.PlotDataItem):

    def __init__(self, *args, display_buffer_size=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSymbolPen(None)
        self.setSymbolBrush(DEFAULT_BRUSH)
        self.setSymbolSize(DEFAULT_SPOT_SIZE)
        # Any pen opts will override the defaults
        if self.opts['pen'] is None:
            if self.opts['symbol'] is not None:
                # Disable line if it's a scatter plot
                self.setPen(None)
            else:
                self.setPen(DEFAULT_PEN)

        # If initialised with no data, initialise with a blank buffer
        if self.getData()[0] is None:
            self.setData(np.zeros(display_buffer_size),
                         np.zeros(display_buffer_size))

    def update_data(self, new_x, new_y):
        # Check input data and find number of new datapoints
        # Both scalars?
        if np.ndim(new_x) == 0 and np.ndim(new_y) == 0:
            num_new_datapoints = 1
        # Both arrays?
        elif isinstance(new_x, np.ndarray) and isinstance(new_y, np.ndarray):
            if new_x.size != new_y.size:
                raise Exception("new_x and new_y must be the same size")
            else:
                num_new_datapoints = new_x.size
        else:
            raise Exception("new_x and new_y must be both scalars or both \
                            arrays")

        # Get the current data
        x, y = self.getData()
        # Move the data to the left
        x = np.roll(x, -num_new_datapoints)
        y = np.roll(y, -num_new_datapoints)
        # Add the most recent data to the end of the array
        x[-num_new_datapoints:] = new_x
        y[-num_new_datapoints:] = new_y
        # Update the data
        self.setData(x, y)


###############################################################################
## Updating plot widget ##
##########################
class UpdatingPlotWidget(pg.PlotWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setMouseEnabled(False, False)
        self.enableAutoRange()
        self.showGrid(x=True, y=True)

    def add_item(self, item_name, *args, **kwargs):
        """
        Add an UpdatingDataItem to the plot.
        `item_name` is used to identify the new item.
        """
        self.addItem(UpdatingDataItem(*args, name=item_name, **kwargs))

    def get_item(self, item_name):
        """
        Return the item in this plot with the given item_name
        """
        for item in self.listDataItems():
            if item.name() == item_name:
                return item

    def get_items(self, item_names):
        """
        Return the item in this plot with the names given in item_names
        """
        items = []
        for item in self.listDataItems():
            if item.name() in item_names:
                items.append(item)
        return items


###############################################################################
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
        new_y = np.random.normal()
        new_x = dataitem.xData[-1] + 1
        dataitem.update_data(new_x, new_y)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update_plot1)
    timer.start(50)

    plot2 = window.addPlot()
    plot2.showGrid(x=True, y=True)
    scatteritem = UpdatingDataItem(a, b, symbol='o')
    plot2.addItem(scatteritem)

    def update_plot2():
        new_a = np.random.normal()
        new_b = np.random.normal()
        scatteritem.update_data(new_a, new_b)

    timer2 = pg.QtCore.QTimer()
    timer2.timeout.connect(update_plot2)
    timer2.start(50)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
