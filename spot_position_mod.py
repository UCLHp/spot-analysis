import numpy as np
from scipy import ndimage
import os
import cv2


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


class ActiveScript:
    def __init__(self, image_dir):
        actscr_loc = os.path.join(os.path.dirname(image_dir),
                                  'activescript.txt')
        for line in open(actscr_loc, 'r'):
            if line.startswith('CameraHRa'):
                CameraHRatio = float(line.split("=")[1].strip())
            if line.startswith('CameraVRa'):
                CameraVRatio = float(line.split("=")[1].strip())
            if line.startswith('AppXCenter'):
                AppXCenter = float(line.split("=")[1].strip())
            if line.startswith('AppYCenter'):
                AppYCenter = float(line.split("=")[1].strip())
            if line.startswith('TextPath'):
                if '3' in line:
                    self.device = '3000'
                if '4' in line:
                    self.device = '4000'
                else:
                    self.device = 'Unknown'
        if self.device == '4000':
            self.CameraHRatio = CameraVRatio
            self.CameraVRatio = CameraHRatio
            self.AppXCenter = AppYCenter
            self.AppYCenter = AppXCenter
        else:
            self.CameraHRatio = CameraHRatio
            self.CameraVRatio = CameraVRatio
            self.AppXCenter = AppXCenter
            self.AppYCenter = AppYCenter


class Profile:
    def __init__(self, profile):
        self.lgrad, self.rgrad = gradient_fetch(profile, 0.2, 0.8)
        self.fwhm = fwhm_fetch(profile)

    def __str__(self):
        return f'lgrad: {self.lgrad}, rgrad: {self.rgrad}, fwhm: {self.fwhm}'


class Spot:
    '''Defines an individual spot (from an array) and it's relevant properties
    as obtained from a LOGOS detector with an activescript.txt file
    '''
    def __init__(self, spot_array, pixel_loc, activescript):
        self.pixel_loc = pixel_loc
        horprof, vertprof, tl_br, bl_tr = spot_to_profiles(spot_array, activescript)

        self.horprof = Profile(horprof)
        self.vertprof = Profile(vertprof)
        self.tl_br = Profile(tl_br)
        self.bl_tr = Profile(bl_tr)

        x = self.pixel_loc[0] - activescript.AppXCenter
        y = self.pixel_loc[1] - activescript.AppYCenter
        x = x / activescript.CameraHRatio
        y = y / activescript.CameraVRatio

        self.rel_pixel_loc = [x, y]

    def __str__(self):
        return f'horprof: {self.horprof}\nvertprof: {self.vertprof}\n'\
               f'tl_br: {self.tl_br}\n bl_tr: {self.bl_tr}\n'\
               f'pixel_loc: {self.pixel_loc}\n'\
               f'rel_pixel_loc: {self.rel_pixel_loc}\n'


class SpotPattern:
    '''Class to define spot pattern images acquired using the flat LOGOS panels
    '''
    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            print('No image selected, code will terminate')
            input('Press any key to continue')
            raise SystemExit

        image_dir = os.path.dirname(image_path)

        if not os.path.isfile(os.path.join(image_dir, 'activescript.txt')):
            print('No active script detected for this spot pattern')
            input('Press any key to continue')
            raise SystemExit

        self.path = image_path
        self.activescriptpath = os.path.join(image_dir, 'activescript.txt')
        self.activescript = ActiveScript(self.activescriptpath)
        self.image = cv2.imread(image_path)

        if self.activescript.device == '4000':
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def __str__(self):
        return f'path: {self.path}\nact_scr_path: {self.activescriptpath}'


def spot_to_profiles(myimage, activescript):
    '''Extract cartesian and diagonal profiles from spot array'''
    blurred = cv2.GaussianBlur(myimage, (11, 11), 0)
    normed = blurred/blurred.max()

    (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(blurred)
    horprof = [range(len(normed[0])), normed[max_loc[1]]]
    vertprof = [range(len(normed)), [x[max_loc[0]] for x in normed]]
    spin_ccw = rotate_image(normed, 45, max_loc)
    spin_cw = rotate_image(normed, -45, max_loc)
    # Top left to bottom right profile
    tl_br = [range(len(spin_ccw[0])), spin_ccw[max_loc[1]]]
    # Bottom left to top right profile
    bl_tr = [range(len(spin_cw[0])), spin_cw[max_loc[1]]]
    horprof[0] = [x/activescript.CameraHRatio for x in horprof[0]]
    vertprof[0] = [x/activescript.CameraVRatio for x in vertprof[0]]

    # Diagonal profile correction to distance from pixel size uses mean of xy
    diag_ratio = (activescript.CameraHRatio + activescript.CameraVRatio) / 2
    tl_br[0] = [x/diag_ratio for x in tl_br[0]]
    bl_tr[0] = [x/diag_ratio for x in bl_tr[0]]

    return horprof, vertprof, tl_br, bl_tr


def gradient_fetch(profile, lowthresh, highthresh):
    '''Takes a gaussian profile as input and returns the gradient on the left
    and right side of the peak between the high threshold and low threshold
    '''
    left_low = [n for n, i in enumerate(profile[1]) if i > lowthresh][0]
    right_low = [n for n, i in enumerate(profile[1]) if i > lowthresh][-1]
    left_high = [n for n, i in enumerate(profile[1]) if i > highthresh][0]
    right_high = [n for n, i in enumerate(profile[1]) if i > highthresh][-1]
    lgrad = 100*(highthresh-lowthresh)/(profile[0][left_high] - profile[0][left_low])
    rgrad = 100*(highthresh-lowthresh)/(profile[0][right_high] - profile[0][right_low])
    return lgrad, rgrad


def fwhm_fetch(profile):
    '''Returns FWHM for a gaussian profile'''
    norm_profile = profile/max(profile[1])
    fwhml = [n for n, i in enumerate(norm_profile[1]) if i > 0.5][0]
    fwhmr = [n for n, i in enumerate(norm_profile[1]) if i > 0.5][-1]
    fwhm = profile[0][fwhmr]-profile[0][fwhml]
    return fwhm


# spotpat = SpotPattern('C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Grids\\2021_0309_0045\\00000001.tif')

# print(spotpat)
