import numpy as np
from scipy.odr import ODR, Model, RealData
from typing import List, Union
from scipy.stats import chi2
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator


class Fit:

    def __init__(self,
                 data: np.ndarray,
                 colorder: List[int],
                 p0: Union[List[float], np.ndarray],
                 func,
                 method: str = 'odr'):

        """
        :param colorder: [x_col, dx_col, y_col, dy_col]
        """
        plt.rcParams['font.size'] = 30

        self.npoints = data.shape[0]
        self.ncols = data.shape[1]

        self.x = data[:, colorder[0]].astype(np.float)
        self.y = data[:, colorder[2]].astype(np.float)

        if colorder[3] is None:
            self.dy = None
        else:
            self.dy = data[:, colorder[3]].astype(np.float)

        self.fitting_func = func

        self.init_params = p0
        self.method = method


        if self.ncols >= 4 and self.method == 'odr':  # ODR
            self.dx = data[:, colorder[1]].astype(np.float)

            self.data = RealData(self.x, self.y, self.dx, self.dy)  # Inserting data to a form which ODR class accepts

            self.model = Model(self.fitting_func)  # Inserting the fitting function to a form which ODR class accepts

            self.odr = ODR(self.data, self.model, self.init_params)  # Creating the ODR instance with initial guesses for the parameters

            self.output = self.odr.run()  # Fit calculations

            self.ep = self.output.beta  # List of estimated fitting parameters

            self.sd_ep = self.output.sd_beta  # List of standard deviation of estimated fitting parameters

            self.yfit = self.fitting_func(self.ep, self.x)  # Fitting function with estimated fitting params
            self.yfit_residuals = self.fitting_func(self.ep, self.x)

            self.chi2 = self.output.sum_square

        elif self.method == 'ls':  # Least Squares
            self.ep, self.cov_ep = curve_fit(self.fitting_func, self.x, self.y, p0=self.init_params, sigma=self.dy)  # Estimated fitting params and their covariance matrix
            self.sd_ep = np.sqrt(np.diag(self.cov_ep))  # List of standard deviation of estimated fitting parameters

            self.yfit = self.fitting_func(self.x, *self.ep)  # Fitting function with estimated fitting params
            self.yfit_residuals = self.fitting_func(self.x, *self.ep)

            if self.dy is None:
                self.chi2 = np.sum((self.yfit_residuals - self.y) ** 2)
            else:
                self.chi2 = np.sum(((self.yfit_residuals - self.y) / self.dy) ** 2)

        else:
            raise ValueError("To run ODR you must define dx and 'method' must be 'odr'\n"
                             "To run Least Squares 'method' must be 'ls'")

        self.dof = len(self.x) - len(self.ep)
        self.pvalue = chi2.sf(self.chi2, self.dof)
        self.chi2red = self.chi2/self.dof

    def __str__(self):
        str = ''
        for i, a in enumerate(self.ep):
            str += f'a[{i}] = {a} +- {self.sd_ep[i]} ({abs(self.sd_ep[i]*100/a):.2f}% Relative Error)\n'

        str += f'\nDoF = {self.dof:.2f}\n'
        str += f'chi squared = {self.chi2:.2f}\n'
        str += f'pvalue = {self.pvalue:.2f}\n'
        str += f'chi squared reduced = {self.chi2red:.2f}\n'
        str += f'\nInitial Parameters = {self.init_params}'

        return str

    def plot_fit(self,
                 title: str,
                 xlabel: str,
                 ylabel:str,
                 fit_num: int
                 ):

        fig, ax = plt.subplots(figsize=(15, 12), num=f'Fit {fit_num}; fit')

        if self.method == 'odr':
            ax.errorbar(self.x, self.y, yerr=self.dy, xerr=self.dx, ls='None', capsize=10, elinewidth=3, fmt='.', ms=30, capthick=3, label='Data')
        elif self.method == 'ls':
            ax.errorbar(self.x, self.y, yerr=self.dy, ls='None', capsize=10, elinewidth=3, fmt='.', ms=30, capthick=3, label='Data')

        ax.plot(self.x, self.yfit, lw=5, label='Fit')
        ax.set(title=fr'${title}$', xlabel=fr'${xlabel}$', ylabel=fr'${ylabel}$')
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.grid()
        ax.legend(loc='best')
        plt.tight_layout()


    def plot_residuals(self,
                 xlabel: str,
                 ylabel: str,
                 fit_num: int
                 ):

        fig, ax = plt.subplots(figsize=(15, 12), num=f'Fit {fit_num}; Residuals')

        if self.method == 'odr':
            ax.errorbar(self.x, self.y - self.yfit_residuals, yerr=self.dy, xerr=self.dx, ls='None', elinewidth=3, capsize=10, fmt='.', ms=30, capthick=3)

        elif self.method == 'ls':
            ax.errorbar(self.x, self.y - self.yfit_residuals, yerr=self.dy, ls='None', elinewidth=3, capsize=10, fmt='.', ms=30, capthick=3)

        ax.hlines(0, min(self.x), max(self.x), colors='r', lw=4, ls='dashed')

        ax.set(title=r'$Residuals$', xlabel=fr'${xlabel}$', ylabel=fr'${ylabel}$')
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.grid()
        plt.tight_layout()


    def plot_initial_guess(self,
                 xlabel: str,
                 ylabel: str,
                 fit_num: int
                 ):

        fig, ax = plt.subplots(figsize=(15, 12), num=f'Fit {fit_num}; Initial Guess')

        if self.method == 'odr':
            ax.errorbar(self.x, self.y, yerr=self.dy, xerr=self.dx, ls='None', capsize=2, elinewidth=1, fmt='.', ms=30, label='Data')
            ax.plot(self.x, self.fitting_func(self.init_params, self.x), lw=1, label='Initial Guess')

        elif self.method == 'ls':
            ax.errorbar(self.x, self.y, yerr=self.dy, ls='None', capsize=2, elinewidth=1, fmt='.', ms=30, label='Data')
            ax.plot(self.x, self.fitting_func(self.x, *self.init_params), lw=5, label='Initial Guess')

        ax.set(title=r'$Initial\ Guess$', xlabel=fr'${xlabel}$', ylabel=fr'${ylabel}$')
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.grid()
        ax.legend(loc='best')
        plt.tight_layout()

