from tkinter import Tk
from tkinter.filedialog import askopenfilename
# tkinter used rather than easygui to minimise need for external libraries

import matplotlib.pyplot as plt
# Used for ROI sanity check plot - could do without?

import logos_module as lm


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

    uniformity_array = lm.image_to_array(image_loc, norm=True)

    ROI, ROI_display = lm.uniformity_ROI(uniformity_array, threshold)

    plt.imshow(ROI_display)
    plt.show()

    uniformity = 100 * ((ROI.max() - ROI.min()) / (ROI.max() + ROI.min()))

    print(f'uniformity is {uniformity}%')
    # labeled_arr, num_roi = measure.label(bw, return_num=True)
    # regionprops = measure.regionprops(labeled_arr, edges)
    # print(dir(regionprops))


if __name__ == '__main__':
    uniformity()
