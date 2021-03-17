import easygui as eg
from astropy.modeling import models, fitting
import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.ndimage import median_filter

import logos_module as lm

def plot3D(data):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x = np.asarray(range(0,data.shape[1]))
    y = np.asarray(range(0,data.shape[0]))
    x, y = np.meshgrid(x, y)
    surf = ax.plot_surface(x,y, data, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

def plot3D_2(x, y, data):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x,y, data, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

@models.custom_model
def doubl_gaus(x, y, amplitude=1, x_mean=0, y_mean=0, theta=0, sigma_x1=1, sigma_y1=1, sigma_x2=1, sigma_y2=1):
    '''
    Equation to calculate two overlapping 2-Dimensional point spread functions
    Both PSFs have the same centre and degree of rotation for simplicity
    but have a major and minor sigma and different amplitudes
    '''

    x_mean = float(x_mean)
    y_mean = float(y_mean)
    a = (np.cos(theta)**2)/(2*sigma_x1**2) + (np.sin(theta)**2)/(2*sigma_y1**2)
    b = -(np.sin(2*theta))/(4*sigma_x1**2) + (np.sin(2*theta))/(4*sigma_y1**2)
    c = (np.sin(theta)**2)/(2*sigma_x1**2) + (np.cos(theta)**2)/(2*sigma_y1**2)
    d = (np.cos(theta)**2)/(2*sigma_x2**2) + (np.sin(theta)**2)/(2*sigma_y2**2)
    e = -(np.sin(2*theta))/(4*sigma_x2**2) + (np.sin(2*theta))/(4*sigma_y2**2)
    f = (np.sin(theta)**2)/(2*sigma_x2**2) + (np.cos(theta)**2)/(2*sigma_y2**2)
    return amplitude*np.exp(-(a*((x-x_mean)**2) + 2*b*(x-x_mean)*(y-y_mean) + c*((y-y_mean)**2))) + (1-amplitude)*np.exp(-(d*((x-x_mean)**2) + 2*e*(x-x_mean)*(y-y_mean) + f*((y-y_mean)**2)))


def create_fits(imagearray, central_pixel, pixeldimensions):
    fit_p = fitting.SLSQPLSQFitter()
    maxpix = 42877
    singl_gaus_mod = models.Gaussian2D(amplitude=1,
                                       x_mean=0,
                                       y_mean=0,
                                       bounds={'amplitude': (0.7 * maxpix, 1.3 * maxpix),
                                               'theta': (-1.58, 1.58)}
                                       )

    doubl_gaus_mod = doubl_gaus(amplitude=1,
                                x_mean=0,
                                y_mean=0,
                                sigma_x1=1,
                                sigma_y1=1,
                                bounds={'amplitude': (0.7 * maxpix, maxpix),
                                        'sigma_x1': (1E-9, 100),
                                        'sigma_y1': (1E-9, 100),
                                        'sigma_x2': (1E-9, 100),
                                        'sigma_y2': (1E-9, 100),
                                        'theta': (-1.58, 1.58)
                                        }
                                )

    x, y = np.meshgrid(np.arange(0, len(imagearray[0])),
                       np.arange(0, len(imagearray))
                       )
    x = np.true_divide(x - central_pixel[0], pixeldimensions[0])
    y = np.true_divide(y - central_pixel[1], pixeldimensions[1])

    normarray = imagearray/maxpix
    print(np.amax(normarray))
    plot3D_2(x, y, normarray)
    print('Fitting Single Gaussian')
    p1 = fit_p(singl_gaus_mod, x, y, normarray, verblevel=0)
    print('Fitting Double Gaussian')
    p2 = fit_p(doubl_gaus_mod, x, y, normarray, verblevel=0)

    singlefit = p1
    singlefitarray = p1(x,y)
    doublefit = p2
    doublefitarray = p2(x, y)

    return [singlefitarray, p1], [doublefitarray, p2]




spotdir = eg.fileopenbox('Select spot to be analysed')
spot = lm.image_to_array(spotdir)

singlefitarray, doublefitarray = create_fits(spot, [790,585], [3.603,3.612])

plot3D(spot)

print()
print(singlefitarray[1])
plot3D(singlefitarray[0])
