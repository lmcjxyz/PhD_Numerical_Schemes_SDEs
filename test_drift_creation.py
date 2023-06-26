#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 13:49:52 2023

@author: lmcj
"""

# %% Imports
import numpy as np
import matplotlib.pyplot as plt
import time
import math as m
from numpy.random import default_rng
from dsdes import approximate, bridge, coarse_noise, create_drift_function,\
        fbm, gen_solve, heat_kernel_var, mv_solve,\
        integral_between_grid_points, solve, solves, create_drift_array
from scipy.integrate import quad_vec
from scipy.stats import norm, linregress
from scipy.stats import linregress

rng = default_rng()

# %% Testing
# QOL parameters
plt.rcParams['figure.dpi'] = 500

# Variables to modify for the scheme
epsilon = 10e-6
beta = 1/16
hurst = 1 - beta
time_steps_max = 2**17
time_steps_approx0 = 2**7
time_steps_approx1 = 2**10
time_steps_approx2 = 2**11
time_steps_approx3 = 2**12
time_steps_approx4 = 2**13
time_steps_approx5 = 2**14
time_steps_approx6 = 2**15
time_steps_list = [time_steps_max,
                   time_steps_approx1,
                   time_steps_approx2,
                   time_steps_approx3,
                   time_steps_approx4,
                   time_steps_approx5,
                   time_steps_approx6]
# Variables to create fBm
points_x = 2**12
half_support = 10
delta_x = half_support/(points_x-1)
grid_x = np.linspace(start=-half_support, stop=half_support, num=points_x)
# For the Brownian bridge
grid_x0 = np.linspace(start=0, stop=2*half_support, num=points_x)
fbm_array = fbm(hurst, points_x, half_support)
bridge_array = bridge(fbm_array, grid_x0)
smooth_array = np.sin(grid_x)
#smooth_array = grid_x

#%%
var_heat_kernel_real = heat_kernel_var(time_steps_max, hurst)
var_heat_kernel_approx0 = heat_kernel_var(time_steps_approx0, hurst)
var_heat_kernel_approx1 = heat_kernel_var(time_steps_approx1, hurst)
var_heat_kernel_approx2 = heat_kernel_var(time_steps_approx2, hurst)
var_heat_kernel_approx3 = heat_kernel_var(time_steps_approx3, hurst)
var_heat_kernel_approx4 = heat_kernel_var(time_steps_approx4, hurst)
var_heat_kernel_approx5 = heat_kernel_var(time_steps_approx5, hurst)
var_heat_kernel_approx6 = heat_kernel_var(time_steps_approx6, hurst)

integral_array_real = integral_between_grid_points(
    var_heat_kernel_real,
    grid_x, half_support)
integral_array0 = integral_between_grid_points(
    var_heat_kernel_approx0,
    grid_x, half_support)
integral_array1 = integral_between_grid_points(
    var_heat_kernel_approx1,
    grid_x, half_support)
integral_array2 = integral_between_grid_points(
    var_heat_kernel_approx2,
    grid_x, half_support)
integral_array3 = integral_between_grid_points(
    var_heat_kernel_approx3,
    grid_x, half_support)
integral_array4 = integral_between_grid_points(
    var_heat_kernel_approx4,
    grid_x, half_support)
integral_array5 = integral_between_grid_points(
    var_heat_kernel_approx5,
    grid_x, half_support)
integral_array6 = integral_between_grid_points(
    var_heat_kernel_approx6,
    grid_x, half_support)

# %%
drift_array_real = create_drift_array(bridge_array, integral_array_real)
drift_array0 = create_drift_array(bridge_array, integral_array0)
drift_array1 = create_drift_array(bridge_array, integral_array1)
drift_array2 = create_drift_array(bridge_array, integral_array2)
drift_array3 = create_drift_array(bridge_array, integral_array3)
drift_array4 = create_drift_array(bridge_array, integral_array4)
drift_array5 = create_drift_array(bridge_array, integral_array5)
drift_array6 = create_drift_array(bridge_array, integral_array6)

# %%
manually_computed_sin = m.exp(
    -heat_kernel_var(time_steps_max, hurst)/2
    )*np.cos(grid_x)
manually_computed_cos = m.exp(
    -heat_kernel_var(time_steps_max, hurst)/2
    )*np.sin(grid_x)

# %% Plots
limy = 5
drift_fig = plt.figure('drift')
plt.plot(grid_x, drift_array_real, label="drift real solution")
#plt.plot(grid_x, manually_computed_sin, label="drift for sin instead of fbm")
# plt.plot(grid_x, manually_computed_cos, label="drift for cos instead of fbm")
plt.plot(grid_x, drift_array0, label="drift approximation 0")
plt.plot(grid_x, drift_array1, label="drift approximation 1")
#plt.plot(grid_x, drift_array2, label="drift approximation 2")
#plt.plot(grid_x, drift_array3, label="drift approximation 3")
#plt.plot(grid_x, drift_array4, label="drift approximation 4")
#plt.plot(grid_x, drift_array5, label="drift approximation 5")
#plt.plot(grid_x, drift_array6, label="drift approximation 6")
plt.ylim([-limy, limy])
plt.legend()
plt.show()

#%% Plots
plt.plot(integral_array0)
plt.plot(integral_array1)
plt.plot(integral_array6)
plt.show()
# %% New potential function for derivative of heat kernel
# testing function
# move to dsdes.py if useful
def derivative_heat_kernel(heat_kernel_var, grid_x, **kwargs):
    constant = -1/(m.sqrt(2*m.pi)*heat_kernel_var)
    sqrt_heat_kernel_var = m.sqrt(heat_kernel_var)
    y = kwargs['y']
    derivative = constant*(grid_x - y)*norm.pdf(grid_x - y,
                                                loc=0,
                                                scale=sqrt_heat_kernel_var)
    return derivative


i, e = quad_vec(derivative_heat_kernel(
    heat_kernel_var=0.01, grid_x=np.linspace(0, 1, 10), y), a=-0.1, b=0.1)
