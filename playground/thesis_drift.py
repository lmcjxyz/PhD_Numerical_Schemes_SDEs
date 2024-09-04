import numpy as np
import matplotlib.pyplot as plt
import thesis_params

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dsdes as ds

rng = np.random.default_rng(seed=1392917848)

hurst = 0.76
time_steps = 2**12

points = 10**3
half_support = 10
gaussian = rng.standard_normal(points)
bn, bH, bB, x = ds.drift(gaussian, hurst, points, half_support, time_steps)

fig, ax = plt.subplots()
ax.plot(x, bH, linewidth='2', color='#2C9BE9', label=r'$B^H$', linestyle=':')
ax.plot(x, bB, linewidth='2', color='#2C9BE9', label=r'$B^H_b$')
ax.plot(x, bn, linewidth='2', color='#FFC622', label=r'$b^N$')
legend = ax.legend()
frame = legend.get_frame()
frame.set_facecolor('lightgray')
frame.set_edgecolor('lightgray')
ax.grid()
plt.show()
