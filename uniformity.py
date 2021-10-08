import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
# tkinter used rather than easygui to minimise need for external libraries

import matplotlib.pyplot as plt
from matplotlib import cm
# Used for ROI sanity check plot - could do without?

import logos_module as lm


def Plot3D(Data):
    fig = plt.figure()  # create the pop up window for the plot
    ax = fig.gca(projection='3d')  # command to change axes properties
    X = np.asarray(range(0, Data.shape[1]))  # create 0-length axis
    Y = np.asarray(range(0, Data.shape[0]))  # create 0-height axis
    X, Y = np.meshgrid(X, Y)  # creates coordinates required to plot
    surf = ax.plot_surface(X, Y, Data, cmap=cm.coolwarm, linewidth=0,
                           antialiased=False)  # creates plot
    fig.colorbar(surf, shrink=0.5, aspect=5)  # makes plot look pretty
    plt.show()


def uniformity(threshold=0.5):
    '''
    Returns uniformity of a rectangular field acquired on a planar LOGOS device

        Parameters:
            threshold(float): where to threshold the image to delect the ROI

        User Input:
            image_loc: user is asked to specify image file location
            Close window: after checking image, user should close the window
        Returns:
            ROI_display(matplotlib): image to confirm ROI on original image
            uniformity(float): central region uniformity metric
                               calculated by ~ 100*(max-min)/(max+min)
    '''
    root = Tk()
    root.withdraw()  # Prevent full gui window from appearing
    image_loc = askopenfilename()  # user selects single uniformity image
    root.destroy()  # Required to allow matplotlib image to pop up and out

    uniformity_array = lm.image_to_array(image_loc)#, norm=True)

    ROI, ROI_display = lm.uniformity_ROI(uniformity_array, uniformity_array.max()/2, inner_reg=0.8)

    plt.imshow(ROI_display)
    plt.show()

    Plot3D(ROI[:, :])

    histlist = ROI.ravel()
    plt.hist(histlist, bins=30, density=True)
    plt.show()
    roi_max = float(ROI.max())
    roi_min = float(ROI.min())
    uniformity = 100*(roi_max-roi_min)/(roi_max+roi_min)
    print(ROI.max())
    print(ROI.min())

    print(f'uniformity is {uniformity}%')
    # labeled_arr, num_roi = measure.label(bw, return_num=True)
    # regionprops = measure.regionprops(labeled_arr, edges)
    # print(dir(regionprops))


if __name__ == '__main__':
    uniformity()
