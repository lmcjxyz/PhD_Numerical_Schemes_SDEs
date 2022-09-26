# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 16:06:58 2022

@author: Luis Mario Chaparro Jáquez

@title: Euler scheme
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy.random import default_rng
rng = default_rng()
from datetime import datetime

class Euler:
    """
    Class used to solve a Stochastic Differential Equation (SDE) using the
    Euler-Maruyama method.

    This will give us the solution to an SDE that satisfies the usual
    assumptions, refer to Kloeden & Platen, Numerical Solutions for Stochastic
    Differential Equations
    """

    def __init__ (
            self, 
            drift, 
            diffusion, 
            time_steps = None,
            time_start = None,
            time_end = None,
            y0 = None, 
            paths = None,
            batches = None
            ):
        """
        Parameters
        ----------
        drift:
            Drift coefficient of the equation, satisfying usual conditions.
        diffusion:
            Diffusion coefficient of the equation, satisfying usual conditions.
        time_steps: int
            The amount of time steps we use to compute the solution, 
            which defines how fine is the grid.
        time_start: float
            The starting time of the scheme.
        time_end: float
            The ending time of the scheme.
        y0: float
            Initial condition for the equation.
        paths: int
            Amount of paths to comput the solution.

        Returns
        -------
        z: float
            A random variable to use in the Euler scheme as the Brownian motion.
        dt:
            The step size in time.
        time_grid: float
            Time grid to compute the solution.
        y: float
            Placeholder for the solution of the SDE.
        """

        # Initialize arguments
        self.drift = drift
        self.diffusion = diffusion
        self.time_steps = time_steps if time_steps \
                is not None else 10**2
        self.time_start = time_start if time_start \
                is not None else 0
        self.time_end = time_end if time_end \
                is not None else 1
        self.y0 = y0 if y0 \
                is not None else 1
        self.paths = paths if paths \
                is not None else 100
        self.batches = batches if batches \
                is not None else 10

        # Time step
        self.dt = self.generate_dt()

        # Creation of normal random variable
        ## Since the time grid would start in t_1, and the random variable
        ## in z_1 we have a bijection between the time grid and each path
        ## of the rv which cannot achieved if we start the time grid in t_0.
        ## Well it can be achieved, but is not what we need given the recursive
        ## nature of the Brownian motion when having coarse grids
        self.z = rng.normal(
                loc = 0.0,
                scale = np.sqrt(self.dt),
                size = (self.time_steps, self.paths, self.batches)
                )
        # Creation of the time grid
        ## We create the time grid starting from the first non-zero term,
        ## effectively we do not need to use the first time (typically 0)
        ## in any moment
        ## Also this is the finest grid, in the solve method we can use this
        ## or a coarser one
        self.time_grid = self.generate_time_grid()
    #############################################################################
    # end of __init__
    #############################################################################

    #############################################################################
    # start of generate_dt
    #############################################################################
    def generate_dt (self, time_steps_dt = None):
        time_steps_dt = time_steps_dt if time_steps_dt \
                is not None else self.time_steps
        time_start_dt = self.time_start
        time_end_dt = self.time_end

        dt_generated = (time_end_dt - time_start_dt) / time_steps_dt
        return dt_generated
    #############################################################################
    # end of generate_dt
    #############################################################################

    #############################################################################
    # start of coarse_z
    #############################################################################
    def coarse_z (self, time_steps_z = None):
        time_steps_z = time_steps_z if time_steps_z \
                is not None else self.time_steps
        z_orig = self.z
        #dt_z = self.generate_dt(time_steps_dt = time_steps_z)
        dt_z = self.dt
        # Placeholder for the new RV
        z_coarse = np.zeros(shape = (time_steps_z, self.paths, self.batches))
        # The amount of elements each element of the coarser noise will have
        # from the finer noise
        # TODO: Make this more robust adding a conditional statement 
        # checking is and integer and smaller than the original time steps, and
        # raising an Error if that does not happen

        # TODO: Change this using numpy.reshape
        n_z = int(np.shape(z_orig)[0] / time_steps_z)
        
        if n_z == 1:
            z_coarse = z_orig
        else:
            temp = z_orig.reshape(
                    time_steps_z, 
                    np.shape(z_orig)[0]//time_steps_z,
                    self.paths,
                    self.batches
                    )
            z_coarse = np.sum(temp, axis=1)
            #for i in range(1, time_steps_z):
            #    #z_coarse[i, :] = dt_z*np.sum(z_orig[(i-1)*n_z:i*n_z], :], axis=0)
            #    z_coarse[i, :] = np.sum(z_orig[(i-1)*n_z:i*n_z, :], axis=0)

        return z_coarse
    #############################################################################
    # end of coarse_z
    #############################################################################

    #############################################################################
    # start of generate_time_grid
    #############################################################################
    def generate_time_grid (self, time_steps_grid = None):
        time_steps_grid = time_steps_grid if time_steps_grid \
                is not None else self.time_steps
        time_start_grid = self.time_start
        time_end_grid = self.time_end

        dt_grid = self.generate_dt( 
                time_steps_dt = time_steps_grid
                )

        time_grid_generated = np.linspace(
                start = time_start_grid + dt_grid, 
                stop = time_end_grid,
                num = time_steps_grid
                )
        return time_grid_generated
    #############################################################################
    # end of generate_time_grid
    #############################################################################

    #############################################################################
    # start of solve
    #############################################################################
    def solve (self, time_steps_solve = None):
        time_steps_solve = time_steps_solve if time_steps_solve \
                is not None else self.time_steps
        time_grid_solve = self.generate_time_grid(time_steps_solve) if time_steps_solve \
                is not None else self.time_grid
        dt_solve = self.generate_dt(time_steps_dt = time_steps_solve) if time_steps_solve \
                is not None else self.dt
        z_solve = self.coarse_z(time_steps_z = time_steps_solve) if time_steps_solve \
                is not None else self.z

        """ Solve the SDE """
        # Creation of the placeholder for the solution.
        self.y = np.zeros(shape = (time_steps_solve, self.paths, self.batches))
        # And adding intial condition.
        self.y[0, :, :] = self.y0

        # You need time_steps_solve - 1 because you have to use
        # i+1 to get the last element
        for i in range(time_steps_solve - 1):
            self.y[i+1, :, :] = self.y[i, :, :] \
                    + self.drift(
                            x = self.y[i, :, :], 
                            t = time_grid_solve[i],
                            m = time_steps_solve
                            )*dt_solve \
                    + self.diffusion(
                            x = self.y[i, :, :],
                            t = time_grid_solve[i],
                            m = time_steps_solve
                            )*z_solve[i+1, :, :]
        return self.y
    #############################################################################
    # end of solve
    #############################################################################

    #############################################################################
    # start of rate
    #############################################################################
    def rate (self, real_solution, approximations, 
            show_plot=False, save_plot=False):
        error = np.zeros(shape=(approximations, self.batches))
        x_axis = np.zeros(approximations)
        length_solution = int(np.log10(np.shape(real_solution)[0]))
        for i in range(approximations):
            m = 10**(length_solution-i-1)
            soln = self.solve(time_steps_solve = m)
            delta = (self.time_end - self.time_start)/m
            #real_solution_coarse = np.zeros(shape = (self.paths, 10**(i+1)))
            real_solution_coarse = real_solution[::10**(i+1), :, :]
            error[i, :] = np.amax(
                            np.mean(
                                np.abs(
                                    np.subtract(real_solution_coarse, soln)
                                    ),
                                axis = 1
                                ),
                            axis=0
                            )
            x_axis[i] = delta
            #print(m**2)
            #print(soln[0, :].T)
            #print(real_solution_coarse[0, :].T)
            #print(np.shape(real_solution_coarse)[1], real_solution_coarse[1, :].T)

            #plt.figure()
            ##plt.plot(soln[:, 1].T)
            ##plt.plot(real_solution_coarse[:, 1].T)
            #plt.plot(soln[:, ])
            #plt.plot(real_solution_coarse[:, ])
            ##plt.plot(soln.T)
            ##plt.plot(real_solution_coarse.T)
            #plt.show()

        error_ic = np.zeros(shape=(2, approximations))
        for i in range(approximations):
            error_var = np.var(error[i, :])
            print(error_var)
            error_sqrt = np.sqrt(error_var/self.batches)
            error_med = np.median(error[i, :])
            error_ic[0, i] = error_med - 1.96*error_sqrt
            error_ic[1, i] = error_med + 1.96*error_sqrt
        #error_ic = np.flip(error_ic, axis=1)
        error_median = np.median(error, axis=1)

        # Consider a system of equations
        # A*p = x
        reg = np.ones(approximations)
        A = np.vstack([np.log10(x_axis), reg]).T
        #A = np.vstack([x_axis, reg]).T
        y_reg = np.log10(error_median[:, np.newaxis])
        #y_reg = error[:, np.newaxis]
        rate, intersection = np.linalg.lstsq(A, y_reg, rcond=None)[0]
        #print(c)


        rate_plot = plt.figure()
        plt.errorbar(
                np.log10(x_axis),
                np.log10(error_median),
                #np.log10(error_ic),
                error_ic,
                label="Error"#, marker="o"
                )
        
        #plt.loglog(x_axis, error, label="Error", marker="o")
        ##plt.plot(
        ##        x_axis, 
        ##        np.log10(intersection) + np.log10(x_axis)*rate,
        ##        linestyle="--",
        ##        label="Rate of convergence: %f"%rate
        ##        )
        plt.title(
                label="Rate = "
                +str(rate)
                +"\nProxy of solution: 10^"+str(length_solution)+" time steps"
                )
        plt.xlabel("Step size")
        plt.ylabel("log(error)")
        plt.legend()

        if show_plot == True:
            plt.show()

        if save_plot == True:
            # For organization reasons the figures are saved into the
            # ./figures_rate/ directory with a time stamp
            rate_plot.savefig(
                    fname = 
                    'figures_rate/'
                    +
                    datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
                    +
                    '_rate'
                    )

        return error_ic, rate#, np.log10(error), np.log10(x_axis)
    #############################################################################
    # end of rate
    #############################################################################

    #############################################################################
    # start of plot_solution
    #############################################################################
    def plot_solution (self, paths_plot, save_plot = False):
        """
        Plot the solutions

        Here you can select the number of paths to plot with paths_plot

        Remember that this method is not very useful in any other situation
        besides testing, its just a sanity check
        """
        solution = plt.figure()
        plt.plot(self.solve()[:, range(paths_plot)])
        plt.title("Euler scheme")
        plt.show()
        if save_plot == True:
            # For organization reasons the figures are saved into the
            # ./figures_solution/ directory with a time stamp
            solution.savefig(
                    fname = 
                    'figures_solution/'
                    +
                    datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
                    +
                    '_solution'
                    )
    #############################################################################
    # end of plot_solution
    #############################################################################
