import numpy as np
from scipy import ndimage
import os

def rotate_image(array, angle, pivot):
    '''Function to rotate an array CCW a given angle around a defined axis
    inputs:
    array - 2D image structure (numpy array )'''
    # Add 0 on both axis such that the pivot is at the centre of the array
    padx = [array.shape[1] - pivot[0], pivot[0]]
    pady = [array.shape[0] - pivot[1], pivot[1]]
    # Add padding to array
    array_p = np.pad(array, [pady, padx], 'constant')
    array_r = ndimage.rotate(array_p, angle, reshape=False)
    return array_r[pady[0]:-pady[1], padx[0]:-padx[1]]
    # further info here: https://stackoverflow.com/questions/25458442/rotate-a-2d-image-around-specified-origin-in-python

class SpotPattern:
    '''Class to define spot pattern images acquired using the flat LOGOS panels
    '''
    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            print('No image selected, code will terminate')
            input('Press any key to continue')
            raise SystemExit

        image_dir = os.path.dirname(imagepath)

        if not os.path.isfile(os.path.join(imagedir,'activescript.txt')):
            print('No active script detected for this spot pattern')
            input('Press any key to continue')
            raise SystemExit

        self.path = imagepath

        self.activescriptpath = os.path.join(imagedir,'activescript.txt')

    def __str__(self):
        return f'path: {self.path}\nact_scr_path: {self.activescriptpath}'



spotpat = SpotPattern('C:\\Users\\cgillies.UCLH\\Desktop\\Coding\\Test_Data\\LOGOS\\Spot_Grids\\2021_0309_0045\\00000001.tif')

print(spotpat)
