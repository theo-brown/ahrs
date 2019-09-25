import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from kalman_filter import KalmanFilter

raw_data = np.loadtxt("barometer_data.txt")
# Truncate raw data (it's super long)
raw_data = raw_data[:raw_data.size//4]
raw_data_step = np.loadtxt("barometer_data_step.txt")
t1 = np.arange(0, raw_data.size/12.5, 1/12.5)
t2 = np.arange(0, raw_data_step.size/12.5, 1/12.5)

fig1 = plt.figure("Data")
ax1 = fig1.add_subplot(121)
ax2 = fig1.add_subplot(122)
fig1.subplots_adjust(bottom=0.25)

[unfiltered_raw_line] = ax1.plot(t1, raw_data)
[unfiltered__step_line] = ax2.plot(t2, raw_data_step)

def filter_data(data, x0, P, Q, R):
    filter1 = KalmanFilter(x0, P, 1, 0, 1, Q, R)
    
    x_out = np.zeros(data.size)
    P_out = np.zeros(data.size)
        
    for k in np.arange(1, data.size):
            x_out[k], P_out[k] = filter1.update(0, data[k])

    return x_out, P_out

P0 = 2
Q0 = 1e-4

[filtered_raw_line] = ax1.plot(t1, filter_data(raw_data, 0, P0, Q0, R=raw_data.var())[0])
[filtered_step_line] = ax2.plot(t2, filter_data(raw_data_step, 0, P0, Q0, R=raw_data.var())[0])

P_slider_ax = fig1.add_axes([0.25, 0.15, 0.65, 0.03])
Q_slider_ax = fig1.add_axes([0.25, 0.1, 0.65, 0.03])

P_slider = Slider(P_slider_ax, 'P', 0.5, 5, valinit=P0)
Q_slider = Slider(Q_slider_ax, 'Q', 1e-4, 1e-3, valinit=Q0)

def sliders_on_changed(val):
    P = P_slider.val
    Q = Q_slider.val
    x_raw_new, P_raw_new = filter_data(raw_data, 0, P, Q, R=raw_data.var())
    filtered_raw_line.set_ydata(x_raw_new)
    x_step_new, P_step_new = filter_data(raw_data_step, 0, P, Q, R=raw_data.var())
    filtered_step_line.set_ydata(x_step_new)

P_slider.on_changed(sliders_on_changed)
Q_slider.on_changed(sliders_on_changed)

plt.show()
