# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 14:13:37 2023

@author: mmlmcj
"""

#%% delete variables
# To delete variables at the start in case we need to reclaim need memory
#from IPython import get_ipython
#ipython = get_ipython()
#ipython.magic("%reset")

#%% packages and parameters
import numpy as np
import matplotlib.pyplot as plt
from numpy.random import default_rng
rng = default_rng()
from scipy.integrate import quad_vec
from scipy.stats import norm, linregress
import time

from dsdes import *

# QOL parameters
plt.rcParams['figure.dpi'] = 500

#%%
##########
# Usage of the functions above to solve multiple SDEs
# and compute convergence rate of approximations
##########

#%% some parameters
# Variables to modify for the scheme
epsilon = 10e-6
beta = 1/8
hurst = 1 - beta
time_steps_max = 2**12
time_steps_approx1 = 2**4
time_steps_approx2 = 2**5
time_steps_approx3 = 2**6
time_steps_approx4 = 2**7
time_steps_approx5 = 2**8

# Variables to create fBm
points_x = 2**8
half_support = 10
delta_x = half_support/(points_x-1)
x_grid = np.linspace(
    start = -half_support, stop = half_support, num = points_x
    )
# For the Brownian bridge
x_grid0 = np.linspace(
    start = 0, stop =2*half_support, num = points_x
    )

# Create an array of fBm
fbm_array = fbm(hurst, points_x, half_support)

# fBm "bridge"
bridge_array = bridge(fbm_array, x_grid0)

# Euler scheme
y0 = 1
sample_paths = 10**5
time_start = 0
time_end = 1

#%% ##### OPTIONAL #####
# Plot fBm
fbm_fig = plt.figure('fbm')
#plt.plot(fbm_array, label='fbm')
plt.plot(x_grid, bridge_array, label='brownian bridge')
plt.grid(linestyle='--', axis='y', linewidth=0.5)
plt.legend()
plt.show()

#%% Create a dF
df_array_real = normal_differences(
    np.sqrt(heat_param(time_steps_max, hurst)),
    points_x, x_grid, half_support)
df_array1 = normal_differences(
    np.sqrt(heat_param(time_steps_approx1, hurst)), 
    points_x, x_grid, half_support)
df_array2 = normal_differences(
    np.sqrt(heat_param(time_steps_approx2, hurst)),
    points_x, x_grid, half_support)
df_array3 = normal_differences(
    np.sqrt(heat_param(time_steps_approx3, hurst)),
    points_x, x_grid, half_support)
df_array4 = normal_differences(
    np.sqrt(heat_param(time_steps_approx4, hurst)),
    points_x, x_grid, half_support)
df_array5 = normal_differences(
    np.sqrt(heat_param(time_steps_approx5, hurst)),
    points_x, x_grid, half_support)

#%% ##### OPTIONAL #####
# Plot dF
df_fig = plt.figure('df')
plt.plot(df_array_real, label="df real solution")
plt.plot(df_array1, label="df approximation 1")
plt.plot(df_array2, label="df approximation 2")
plt.plot(df_array3, label="df approximation 3")
plt.legend()
plt.show()

#%% Create drift by convolution with the bridge
drift_array_real = np.convolve(bridge_array, df_array_real, 'same')
drift_array1 = np.convolve(bridge_array, df_array1, 'same')
drift_array2 = np.convolve(bridge_array, df_array2, 'same')
drift_array3 = np.convolve(bridge_array, df_array3, 'same')
drift_array4 = np.convolve(bridge_array, df_array4, 'same')
drift_array5 = np.convolve(bridge_array, df_array5, 'same')

#%% ##### OPTIONAL ##### Create drift by convolution with the fBm
#drift_array_real = np.convolve(fbm_array, df_array_real, 'same')
#drift_array1 = np.convolve(fbm_array, df_array1, 'same')
#drift_array2 = np.convolve(fbm_array, df_array2, 'same')
#drift_array3 = np.convolve(fbm_array, df_array3, 'same')
#drift_array4 = np.convolve(fbm_array, df_array4, 'same')
#drift_array5 = np.convolve(fbm_array, df_array5, 'same')

#%% ##### OPTIONAL #####
# Plot drift
drift_fig = plt.figure('drift')
plt.plot(x_grid, drift_array_real, label="drift real solution")
plt.plot(x_grid, drift_array1, label="drift approximation 1")
plt.plot(x_grid, drift_array2, label="drift approximation 2")
plt.plot(x_grid, drift_array3, label="drift approximation 3")
plt.legend()
plt.show()

#%% Distance between points in grid for x
delta_x = half_support/(points_x-1)

# Evaluate and plot some drift functions
support = np.linspace(-half_support, half_support, points_x)

#%% ########OPTIONAL##########
eval_real = drift_func(support, drift_array_real, x_grid, points_x, delta_x)
eval1 = drift_func(support, drift_array1, x_grid, points_x, delta_x)
eval2 = drift_func(support, drift_array2, x_grid, points_x, delta_x)
eval3 = drift_func(support, drift_array3, x_grid, points_x, delta_x)
eval4 = drift_func(support, drift_array4, x_grid, points_x, delta_x)
eval5 = drift_func(support, drift_array5, x_grid, points_x, delta_x)

#%% ##### OPTIONAL #####
drift_func_fig = plt.figure('driftfunc')
plt.plot(support, bridge_array, label="fbm")
plt.plot(support, eval_real, label="real solution drift function")
#plt.plot(support, eval1, label="approximation 1 drift function")
#plt.plot(support, eval2, label="approximation 2 drift function")
#plt.plot(support, eval3, label="approximation 3 drift function")
plt.grid()
plt.legend()
plt.show()

#%% #### OPTIONAL ####
# Convolute deterministic functions with dF and plot for testing purposes
# Create a deterministic function for testing
square = x_grid**2
cube = x_grid**3
sine = np.sin(x_grid)
# Create dF, you can change ts to see different parameters of the heat kernel
ts = 2**10
points_x_test = 2**8
x_grid_test = np.linspace(
    start = -half_support, stop = half_support, num = points_x
    )
df_array_det = normal_differences(
    np.sqrt(heat_param(time_steps_approx1, hurst)), 
    #1/10**4,
    points_x_test, x_grid_test, half_support
    )
# Convolute
square_conv = np.convolve(square, df_array_det, 'same')
cube_conv = np.convolve(cube, df_array_det, 'same')
sine_conv = np.convolve(sine, df_array_det, 'same')
# Plot; comment out whatever
det_fig = plt.figure('det_fig')
plt.plot(support, square_conv, label="derivative of square: linear")
plt.plot(support, 2*support, label="linear function")
plt.plot(support, cube_conv, label="derivative of cube: square")
plt.plot(support, 3*support**2, label="square function")
plt.plot(support, sine_conv, label="derivative of sin: cos")
plt.plot(support, np.cos(support), label="cos function")
plt.legend()
#plt.ylim([-5, 5])
plt.show()

#%% Parameters for solution/approximations
# Parameters for real solution
dt_real = (time_end - time_start)/(time_steps_max-1)
time_grid_real = np.linspace(time_start + dt_real, time_end, time_steps_max)
time_grid_real0 = np.insert(time_grid_real, 0, 0)
z_real = rng.normal(loc=0.0, scale=np.sqrt(dt_real), 
                    size=(time_steps_max, sample_paths))

# Parameters for approximation 1
dt_approx1 = (time_end - time_start)/(time_steps_approx1 - 1)
time_grid_approx1 = np.linspace(
    time_start + dt_approx1, time_end, time_steps_approx1
    )
time_grid_approx10 = np.insert(time_grid_approx1, 0, 0)
z_approx1 = coarse_noise(z_real, time_steps_approx1, sample_paths)

# Parameters for approximation 2
dt_approx2 = (time_end - time_start)/(time_steps_approx2 - 1)
time_grid_approx2 = np.linspace(
    time_start + dt_approx2, time_end, time_steps_approx2
    )
time_grid_approx20 = np.insert(time_grid_approx2, 0, 0)
z_approx2 = coarse_noise(z_real, time_steps_approx2, sample_paths)

# Parameters for approximation 3
dt_approx3 = (time_end - time_start)/(time_steps_approx3 - 1)
time_grid_approx3 = np.linspace(
    time_start + dt_approx3, time_end, time_steps_approx3
    )
time_grid_approx30 = np.insert(time_grid_approx3, 0, 0)
z_approx3 = coarse_noise(z_real, time_steps_approx3, sample_paths)

# Parameters for approximation 4
dt_approx4 = (time_end - time_start)/(time_steps_approx4 - 1)
time_grid_approx4 = np.linspace(
    time_start + dt_approx4, time_end, time_steps_approx4
    )
time_grid_approx40 = np.insert(time_grid_approx4, 0, 0)
z_approx4 = coarse_noise(z_real, time_steps_approx4, sample_paths)

# Parameters for approximation 5
dt_approx5 = (time_end - time_start)/(time_steps_approx5 - 1)
time_grid_approx5 = np.linspace(
    time_start + dt_approx5, time_end, time_steps_approx5
    )
time_grid_approx50 = np.insert(time_grid_approx5, 0, 0)
z_approx5 = coarse_noise(z_real, time_steps_approx5, sample_paths)

#%% ##### OPTIONAL #####
# Visualize coarse noises
coarse_fig = plt.figure()
plt.plot(time_grid_approx4, z_approx4[:,0], label="approximation")
plt.plot(time_grid_real, z_real[:,0], label="real solution")
plt.legend()
plt.show()

#%%% Solve an SDE by Euler scheme
st = time.process_time()
real_solution = solves(
    y0,
    drift_array_real,
    z_real,
    time_start,
    time_end,
    time_steps_max,
    sample_paths,
    x_grid,
    points_x,
    delta_x
    )
approx1 = solves(
    y0, 
    drift_array1,
    z_approx1,
    time_start,
    time_end,
    time_steps_approx1,
    sample_paths,
    x_grid,
    points_x,
    delta_x
    )
approx2 = solves(
    y0,
    drift_array2,
    z_approx2,
    time_start,
    time_end,
    time_steps_approx2,
    sample_paths,
    x_grid,
    points_x,
    delta_x
    )
approx3 = solves(
    y0,
    drift_array3,
    z_approx3,
    time_start,
    time_end,
    time_steps_approx3,
    sample_paths,
    x_grid,
    points_x,
    delta_x
    )
approx4 = solves(
    y0,
    drift_array4,
    z_approx4,
    time_start,
    time_end,
    time_steps_approx4,
    sample_paths,
    x_grid,
    points_x,
    delta_x
    )
approx5 = solves(
    y0,
    drift_array5,
    z_approx5,
    time_start,
    time_end,
    time_steps_approx5,
    sample_paths,
    x_grid,
    points_x,
    delta_x
    )
et = time.process_time()
rt = et - st

#%% plot SDE ##### OPTIONAL ##### this doesn't make sense when using "solves"
# Plot solution to SDE
emreal_fig = plt.figure('emreal_fig')
plt.plot(time_grid_real0, real_solution[:, 0:3])
plt.title("real solution")
plt.show()

em1_fig = plt.figure('em2_fig')
plt.plot(time_grid_approx10, approx1[:, 0:3])
plt.title("approximation 1")
plt.show()

em2_fig = plt.figure('em2_fig')
plt.plot(time_grid_approx20, approx2[:, 0:3])
plt.title("approximation 2")
plt.show()

em3_fig = plt.figure('em3_fig')
plt.plot(time_grid_approx30, approx3[:, 0:3])
plt.title("approximation 3")
plt.show()

em4_fig = plt.figure('em4_fig')
plt.plot(time_grid_approx40, approx4[:, 0:3])
plt.title("approximation 4")
plt.show()

em5_fig = plt.figure('em5_fig')
plt.plot(time_grid_approx50, approx5[:, 0:3])
plt.title("approximation 5")
plt.show()

#%% ##### OPTIONAL #####
# Comparing single sample paths of different approximations
emssp_fig = plt.figure('emssp_fig')
plt.plot(time_grid_real0, real_solution[:, 0], label="real solution")
plt.plot(time_grid_approx10, approx1[:, 0], label="approximation 1")
plt.plot(time_grid_approx20, approx2[:, 0], label="approximation 2")
plt.plot(time_grid_approx30, approx3[:, 0], label="approximation 3")
plt.title("single sample path comparison")
plt.legend()
plt.show()

#%% Computation of strong errors at terminal time
pathwise_error = np.zeros(shape=(5, sample_paths))
pathwise_error[0, :] = np.abs(real_solution[-1, :] - approx1[-1, :])
pathwise_error[1, :] = np.abs(real_solution[-1, :] - approx2[-1, :])
pathwise_error[2, :] = np.abs(real_solution[-1, :] - approx3[-1, :])
pathwise_error[3, :] = np.abs(real_solution[-1, :] - approx4[-1, :])
pathwise_error[4, :] = np.abs(real_solution[-1, :] - approx5[-1, :])

strong_error = np.mean(pathwise_error, axis=1)
# error bars
a = 5
seci = np.zeros(shape=a)
for i in range(a):
    seci[i] = 1.96*np.sqrt(np.sum((pathwise_error[i, :] - strong_error[i])**2/(sample_paths-1))/sample_paths)

#%% weak error
# Computation of weak errors at terminal time
pw_weak_error = np.zeros(shape=(5, sample_paths))
pw_weak_error[0, :] = real_solution[-1, :] - approx1[-1, :]
pw_weak_error[1, :] = real_solution[-1, :] - approx2[-1, :]
pw_weak_error[2, :] = real_solution[-1, :] - approx3[-1, :]
pw_weak_error[3, :] = real_solution[-1, :] - approx4[-1, :]
pw_weak_error[4, :] = real_solution[-1, :] - approx5[-1, :]
#pw_weak_error[5, :] = real_solution[-1, :] - approx6[-1, :]
#pw_weak_error[6, :] = real_solution[-1, :] - approx7[-1, :]

weak_error = np.abs(np.mean(pw_weak_error, axis=1))
# error bars
a = 5
weci = np.zeros(shape=a)
for i in range(a):
    weci[i] = 1.96*np.sqrt(
        np.sum(
            (pw_weak_error[i, :] - weak_error[i])**2/(sample_paths-1)
            )/sample_paths
        )

#%% consecutive strong error
# Errors between consecutive approximations
pw_consecutive_error = np.zeros(shape=(4, sample_paths))
pw_consecutive_error[0, :] = np.abs(approx2[-1, :] - approx1[-1, :])
pw_consecutive_error[1, :] = np.abs(approx3[-1, :] - approx2[-1, :])
pw_consecutive_error[2, :] = np.abs(approx4[-1, :] - approx3[-1, :])
pw_consecutive_error[3, :] = np.abs(approx5[-1, :] - approx4[-1, :])
#pw_consecutive_error[4, :] = np.abs(approx6[-1, :] - approx5[-1, :])
#pw_consecutive_error[5, :] = np.abs(approx7[-1, :] - approx6[-1, :])

consecutive_strong_error = np.mean(pw_consecutive_error, axis=1)
# error bars
b = 4
cseci = np.zeros(shape=b)
for i in range(b):
    cseci[i] = 1.96*np.sqrt(
        np.sum(
            (pw_consecutive_error[i, :] - consecutive_strong_error[i])**2/(sample_paths-1)
            )/sample_paths
        )

#%% consecutive weak error
# Bias between consecutive approximations
pw_consecutive_bias = np.zeros(shape=(4, sample_paths))
pw_consecutive_bias[0, :] = approx2[-1, :] - approx1[-1, :]
pw_consecutive_bias[1, :] = approx3[-1, :] - approx2[-1, :]
pw_consecutive_bias[2, :] = approx4[-1, :] - approx3[-1, :]
pw_consecutive_bias[3, :] = approx5[-1, :] - approx4[-1, :]
#pw_consecutive_bias[4, :] = approx6[-1, :] - approx5[-1, :]
#pw_consecutive_bias[5, :] = approx7[-1, :] - approx6[-1, :]

consecutive_bias = np.mean(pw_consecutive_bias, axis=1)
consecutive_weak_error = np.abs(consecutive_bias)
# error bars
b = 4
cweci = np.zeros(shape=b)
for i in range(b):
    cweci[i] = 1.96*np.sqrt(
        np.sum(
            (pw_consecutive_bias[i, :] - consecutive_weak_error[i])**2/(sample_paths-1)
            )/sample_paths
        )

#%% rate of convergence
deltas = [(time_end - time_start)/time_steps_approx1,
          (time_end - time_start)/time_steps_approx2,
          (time_end - time_start)/time_steps_approx3,
          (time_end - time_start)/time_steps_approx4,
          (time_end - time_start)/time_steps_approx5
          #,
          #(time_end - time_start)/time_steps_approx6,
          #(time_end - time_start)/time_steps_approx7
          ] 

log_strong_error = np.log10(strong_error)
log_weak_error = np.log10(weak_error)
log_deltas = np.log10(deltas)

reg_strong = linregress(log_deltas, log_strong_error)
rate_strong = reg_strong.slope
intersection_strong = reg_strong.intercept
print(rate_strong)

reg_weak = linregress(log_deltas, log_weak_error)
rate_weak = reg_weak.slope
intersection_weak = reg_weak.intercept
print(rate_weak)

#%% Several plots ##### OPTIONAL #####

#%% all errors plot
both_error_fig = plt.figure('both_error_fig')
plt.title("errors for beta=%.5f \n strong error rate = %f \n weak error rate = %f" % (beta, rate_strong, rate_weak))
plt.errorbar([0, 1, 2, 3, 4], strong_error, yerr=seci, marker='', linewidth=1, label='strong error')
plt.errorbar([0, 1, 2, 3, 4], weak_error, yerr=weci, marker='', linewidth=1, label='weak error')
plt.errorbar([0.5, 1.5, 2.5, 3.5], consecutive_strong_error, yerr=cseci, marker='', linewidth=1, label='error between consecutive approximations')
plt.errorbar([0.5, 1.5, 2.5, 3.5], consecutive_weak_error, yerr=cweci, marker='', linewidth=1, label='bias between consecutive approximations')
#plt.semilogy([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], consecutive_strong_error, marker='o', label='error between consecutive approximations')
#plt.semilogy([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], consecutive_weak_error, marker='o', label='bias between consecutive approximations')
plt.yscale('log')
plt.legend()
plt.show()

#%% strong error plot
rate_fig = plt.figure('rate_fig')
plt.title("strong error")
plt.semilogy(strong_error, marker='o')
plt.show()

#%% consecutive error plot
consecutive_error_fig = plt.figure('consecutive_error_fig')
plt.title("error between consecutive approximations")
plt.semilogy(strong_error, marker='o')
plt.show()

#%% one sample path
path = 9
plt.figure('paths')
plt.plot(t0_real, real_solution[:,path])
plt.plot(t0_a1,         approx1[:,path])
plt.plot(t0_a2,         approx2[:,path])
plt.plot(t0_a3,         approx3[:,path])
plt.plot(t0_a4,         approx4[:,path])
plt.plot(t0_a5,         approx5[:,path])
plt.show()

#%% histograms
fig, ax = plt.subplots()
ax.hist(real_solution[1,:], bins=30)
ax.hist(approx1[1,:], bins=30)
plt.show()


#%% ##### OPTIONAL #####
# Plot of strong error
rate_fig = plt.figure('rate_fig')
plt.semilogy(strong_error, marker='o')
plt.show()

#%% ##### OPTIONAL #####
# Printing errors and CIs
print(strong_error)
print(seci)
print(weak_error)
print(weci)
print(consecutive_strong_error)
print(cseci)
print(consecutive_bias)
print(cweci)































