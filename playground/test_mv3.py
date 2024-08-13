import numpy as np
import pde
from numpy.random import default_rng
import matplotlib.pyplot as plt
from scipy.stats import norm
import time

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dsdes as ds

start_time = time.time()

rng = default_rng()

plt.rcParams['figure.dpi'] = 200

# Parameters for Euler scheme
time_steps = 2**9
epsilon = 10e-6
beta = 1/4 - epsilon
hurst = 1 - beta
y0 = 1
sample_paths = 10**4
time_start = 0
time_end = 1
dt = (time_end - time_start)/(time_steps - 1)
time_grid = np.linspace(time_start + dt, time_end, time_steps)

noise = rng.normal(
        loc=0.0, scale=np.sqrt(dt),
        size=(time_steps, sample_paths)
        )

# Parameters to create fBm and drift
# These are also for the space paramenter of the PDE
points_x = 2**8  # According to the lower bound in the paper
half_support = 10

eta = 1/((hurst-1/2)**2 + 2 - hurst)
lower_bound = 2*half_support*time_steps**(eta/2)
eqn = 66
if (points_x <= lower_bound):
    msg = 'You need to define your fBm on at least %.2f \
            points as per equation (%d) in the paper.' % (lower_bound, eqn)
    raise ValueError(msg)
    sys.exit(1)

delta_x = half_support/(points_x-1)
grid_x = np.linspace(start=-half_support, stop=half_support, num=points_x)
grid_x0 = np.linspace(start=0, stop=2*half_support, num=points_x)
fbm_array = ds.fbm(hurst, points_x, half_support)
bridge_array = ds.bridge(fbm_array, grid_x0)

# Variance of heat kernel
var_heat_kernel = ds.heat_kernel_var(time_steps, hurst)

# Integral between grid points
integral_grid = ds.integral_between_grid_points(var_heat_kernel, grid_x, half_support)

# Drift creation
drift_array = ds.create_drift_array(bridge_array, integral_grid)

def drift_f(x: np.ndarray, drift_array=drift_array, grid=grid_x):
    return np.interp(x=x.data, xp=grid, fp=drift_array)

# FP
eq = ds.FokkerPlanckPDE(drift_f, lambda x: np.sin(x))
grid = pde.CartesianGrid(bounds=[(-half_support, half_support)], shape=points_x, periodic=False)
x = np.linspace(-half_support, half_support, points_x) 
ic = norm.pdf(x, loc=1, scale=3)
#ic = np.ones_like(x)
state = pde.ScalarField(grid=grid, data=ic)
storage = pde.MemoryStorage()
eq.solve(state, t_range=(time_start, time_end), solver='scipy',
         tracker=storage.tracker(dt))

# div
div_array = np.multiply(drift_array, np.cos(0.1*np.array(storage.data)))

# plot
plt.plot(drift_array)
plt.plot(div_array[1])
plt.plot(div_array[10])
plt.plot(div_array[100])
plt.show()
