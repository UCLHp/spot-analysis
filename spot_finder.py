import easygui
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import Button
from datetime import datetime
from scipy import ndimage

# global variables are used inside the functions due
# to the way slider.on_changed and button.on_clicked are not allowing arguments in called functions

def rotate_image(array, angle, pivot):
    '''Function to rotate an array CCW a given angle around a defined axis'''
    # Add 0 on both axis such that the pivot is at the centre of the array
    padx = [array.shape[1] - pivot[0], pivot[0]]
    pady = [array.shape[0] - pivot[1], pivot[1]]
    # Add padding to array
    array_p = np.pad(array, [pady, padx], 'constant')
    array_r = ndimage.rotate(array_p, angle, reshape=False)
    return array_r[pady[0]:-pady[1], padx[0]:-padx[1]]
    # further info here: https://stackoverflow.com/questions/25458442/rotate-a-2d-image-around-specified-origin-in-python


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
    horprof[0] = horprof[0]*activescript.CameraHRatio
    vertprof[0] = vertprof[0]*activescript.CameraVRatio
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
    fwhml = [n for n, i in enumerate(profile[1]) if i > 0.5][0]
    fwhmr = [n for n, i in enumerate(profile[1]) if i > 0.5][-1]
    fwhm = profile[0][fwhmr]-profile[0][fwhml]
    return fwhm


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
    def __init__(self, spot_array, pixel_loc, activescript):
        self.pixel_loc = pixel_loc
        horprof, vertprof, tl_br, bl_tr = spot_to_profiles(spot_array)

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



# this fucntion opens the spot image, converts it into grayscale and blurs it
def image_open_blur():
    global original
    global blurred
    global activescript
    # read image
    image_path = easygui.fileopenbox("Please pick a spot image :")
    activescript = ActiveScript(image_path)

    original = cv2.imread(image_path)

    if activescript.device == '4000':
        original = cv2.rotate(original, cv2.ROTATE_90_COUNTERCLOCKWISE)

    print("\nImage dimensions are", original.shape)

    # for repetitive testing purposes
    # original=cv2.imread("HawkXYPattern.tiff")

    # convert into grayscale
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # blur with Gaussian kernel
    # !!experiment with kernel size, maybe make it image size dependent
    blurred = cv2.GaussianBlur(gray, (51, 51), 0, cv2.BORDER_ISOLATED)

    # plot histogram
    # plt.hist (gray,100,histtype='step')
    # plt.show()


# this function process the image and creates the three subplots.
# It will be used for the first iteration and when a button is pressed.
# When a slider is moved instead, the similar function image_reprocessing_plotting below
# will be used due to the way it gets values from the sliders.
def image_processing_plotting(threshold, specificity, max_detection_size, nearest_circles, scaling, font_size):

    global thresholded
    global eroded
    global dilated
    global circled
    global circles

    # thresholding
    thresholded = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)[1]

    # Erosion and dilation
    eroded = cv2.erode(thresholded, None, iterations=2)
    dilated = cv2.dilate(eroded, None, iterations=2)

    # detect circles in the thresholded image
    # 4th parameter: minimum distance between circles,
    # 6th parameter: lowering it increases the sensitivity but decreases the specificity
    circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, nearest_circles,
                               param1=50, param2=specificity, minRadius=0, maxRadius=int(max_detection_size))

    # Order spots by grid position, y is rounded to nearest 10 to enable sort
    circles = np.asarray(sorted(circles[0], key=lambda k: [int(round(k[1], -2)), int(k[0])]))
    # Need to expand dimensions to match previous data structure
    circles = np.expand_dims(circles, axis=0)
    # create a copy of the original image to be circled
    # ??ask why circled=original doesn't work and original is also modified
    circled = original.copy()

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles
        i = 0
        for (x, y, r) in circles:
            i += 1
            # draw the circles over the original image
            cv2.circle(circled, (x, y), int(r*scaling), (0, 255, 0), 4)
            cv2.putText(circled, str(i), (x-int(r*scaling), y), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 0, 0),3)


    plt.subplots_adjust(bottom=0.50)

    plt.subplot(131)
    plt.imshow(original)
    plt.title('Original')

    plt.subplot(132)
    plt.imshow(dilated, cmap='gray')
    plt.title('Thresholded\n& Processed')

    plt.subplot(133)
    plt.imshow(circled, cmap='gray')
    plt.title('Detected Spots')

    plt.show()


# As before but this function will run every time a slider is moved
def image_reprocessing_plotting(val):

    global thresholded
    global eroded
    global dilated
    global circled
    global circles
    global threshold
    global specificity
    global max_detection_size
    global nearest_circles
    global scaling
    global font_size

    # get values from the sliders
    threshold = threshold_slider.val
    specificity = specificity_slider.val
    max_detection_size = max_detection_size_slider.val
    nearest_circles = nearest_circles_slider.val
    scaling = scaling_slider.val

    # thresholding
    thresholded = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)[1]

    # Erosion and dilation
    eroded = cv2.erode(thresholded, None, iterations=2)
    dilated = cv2.dilate(eroded, None, iterations=2)

    # detect circles in the thresholded image
    # 4th parameter: minimum distance between circles,
    # 6th parameter: lowering increases sensitivity + decreases the specificity
    circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, nearest_circles,
                               param1=50, param2=specificity, minRadius=0,
                               maxRadius=int(max_detection_size)
                               )
    # Order spots by grid position, y is rounded to nearest 10 to enable sort
    circles = np.asarray(sorted(circles[0], key=lambda k: [round(k[1], -2), k[0]]))
    # Need to expand dimensions to match previous data structure
    circles = np.expand_dims(circles, axis=0)

    # create a copy of the original image to be circled
    # ??ask why circled=original doesn't work and original is also modified
    circled = original.copy()

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles
        i = 0
        for (x, y, r) in circles:
            i += 1
            # draw the circles over the original image
            cv2.circle(circled, (x, y), int(r*scaling), (0, 255, 0), 4)
            cv2.putText(circled, str(i), (x-int(r*scaling), y), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 0, 0),3)


    plt.subplots_adjust(bottom=0.50)

    plt.subplot(131)
    plt.imshow(original)
    plt.title('Original')

    plt.subplot(132)
    plt.imshow(dilated, cmap='gray')
    plt.title('Thresholded\n& Processed')

    plt.subplot(133)
    plt.imshow(circled, cmap='gray')
    plt.title('Detected Spots')

    plt.show()



# font increase and decrease functions, called when the relevant buttons are pressed
def increase_font(val):
    global font_size
    font_size += 0.5
    image_processing_plotting(threshold, specificity, max_detection_size, nearest_circles, scaling, font_size)


def decrease_font(val):
    global font_size
    if font_size>0.5:
        font_size -= 0.5
        image_processing_plotting(threshold, specificity, max_detection_size, nearest_circles, scaling, font_size)


# spot extraction function, called when the relevant button is pressed
def extract(val):
    spot_data = {}
    if circles is not None:

        # ask user for path and create a timestamped folder to dump the spot images
        # save_path = easygui.diropenbox("Please pick a path to create spot folder :")
        # save_path = (save_path+"\\Exported Spots "+datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        # os.makedirs(save_path)

        # loop over the (x, y) coordinates and radius of the circles
        i = 0
        for (x, y, r) in circles:
            i += 1

            # set the exported image boundaries as a square centred on the spot centre
            y1 = y - int(r * scaling)
            y2 = y + int(r * scaling)
            x1 = x - int(r * scaling)
            x2 = x + int(r * scaling)

            # these checks are performed because when negative numbers are used
            # for y1 and x1, that is when a spot is to the left
            # or at the top of the image,
            # the (partial) spot image saved is corrupted and can't be opened
            # to counter that, negative values are replaced with zeros
            if y1 < 0:
                y1 = 0
            if x1 < 0:
                x1 = 0

            # crop
            crop_img = original[y1:y2, x1:x2]

            spot_data[i] = Spot(crop_img[:,:,0], [x,y], activescript)
            # horprof, vertprof, tl_br, bl_tr = spot_to_profiles(crop_img[:,:,0])
            # fwhm = fwhm_fetch(horprof)
            # gradients = gradient_fetch(horprof, 0.2, 0.8)
            # print(f'fwhm for {i} is {fwhm}, lgrad is {gradients[0]}, rgrad is {gradients[1]}')
            print(i)
            print(spot_data[i])
            # cv2.imwrite((save_path+"\\" + str(i)+".tiff"), crop_img)
        # os.startfile(save_path)

# new spot image load function, called when the relevant button is pressed
def load_new(val):
   image_open_blur()
   image_processing_plotting(threshold, specificity, max_detection_size, nearest_circles, scaling, font_size)


# myfile = easygui.fileopenbox()
# print(fetch_pixel_dimensions(myfile))


image_open_blur()

# initialise values
# !!perhaps calculate initial threshold value based on histogram, e.g. 2% of pixels
# !!perhaps calculate initial max_detection based on image size
def_threshold = 10
threshold = def_threshold

def_specificity = 15
specificity = def_specificity

def_max_detection_size = 100
max_detection_size = def_max_detection_size

def_nearest_circles = 20
nearest_circles = def_nearest_circles

def_scaling = 1
scaling = def_scaling

font_size = 2.1


# plotting sliders and buttons. These are matplotlib widgets.
# For every item, first a corresponding axis is plotted as a placeholder,
# then the item itself is defined
plt.figure("Spot Finder v0.6")

controls_height = 0.32
threshold_ax = plt.axes([0.27, controls_height+0.13, 0.5, 0.02])
specificity_ax = plt.axes([0.27, controls_height+0.1, 0.5, 0.02])
max_detection_size_ax = plt.axes([0.27, controls_height+0.07, 0.5, 0.02])
nearest_circles_ax = plt.axes([0.27, controls_height+0.04, 0.5, 0.02])
scaling_ax = plt.axes([0.27, controls_height+0.01, 0.5, 0.02])

font_dec_ax = plt.axes([0.85, controls_height+0.11, 0.045, 0.05])
font_inc_ax = plt.axes([0.905, controls_height+0.11, 0.045, 0.05])
extract_ax = plt.axes([0.85, controls_height+0.03, 0.1, 0.07])
reload_ax = plt.axes([0.85, controls_height-0.05, 0.1, 0.07])

font_dec_button = Button(font_dec_ax, "Font\n-")
font_inc_button = Button(font_inc_ax, "Font\n+")
extract_button = Button(extract_ax, "Export\nspots")
reload_button = Button(reload_ax, "Load new\nimage")

threshold_slider = Slider(threshold_ax,      # the axes object containing the slider
                  'Threshold',            # the name of the slider parameter
                  0,          # minimal value of the parameter
                  255,          # maximal value of the parameter
                  valinit=def_threshold,  # initial value of the parameter
                valstep=1,  # discrete step size
                valfmt="%1.0f",  # printing format
                dragging=False  # mouse dragging is not allowed for speed reasons
                 )

specificity_slider = Slider(specificity_ax, 'Specificity', 0, 40,
                            valinit=def_specificity, valstep=1, valfmt="%1.0f", dragging=False)

max_detection_size_slider = Slider(max_detection_size_ax, 'Max detection size', 0, 150,
                valinit=def_max_detection_size,valstep=5, valfmt="%1.0f", dragging=False)

nearest_circles_slider = Slider(nearest_circles_ax, 'Min dist between detected circles', 1, 100,
                valinit=def_nearest_circles, valstep=1, valfmt="%1.0f", dragging=False)

scaling_slider = Slider(scaling_ax, 'Extraction size (use last)', 0.4, 5,
                        valinit=def_scaling, valstep=0.2, valfmt="%1.1f", dragging=False)


# plot instructions
plt.text(0.02, 0.1, "Instructions: "
                    "\n1) Change \"Threshold\" until all spots in the thresholded image are visible and separated."
                    "\n2) Decrease \"Specificity\" until all spots are detected."
                    "\n3) Decrease \"Max detection size\" to get rid of large false detections."
                    "\n4) If more than one detections are made within a spot, increase \"Min dist between detected circles\"."
                    "\n5) Once satisfied, select desirable margin for exported spot images using the \"Extraction size\".",
                    fontsize=12, transform=plt.gcf().transFigure)

# maximising with Tkagg backend, other backends will need different code
# see https://stackoverflow.com/questions/32428193/saving-matplotlib-graphs-to-image-as-full-screen
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())


# call the reprocessing function when a slider is moved
# or the relevant button functions
# note that "on_changed" will only work with one function with one float argument
# thus the weird single argument of the function image_processing_plotting. Not sure if it breaks functionality
threshold_slider.on_changed(image_reprocessing_plotting)
scaling_slider.on_changed(image_reprocessing_plotting)
specificity_slider.on_changed(image_reprocessing_plotting)
max_detection_size_slider.on_changed(image_reprocessing_plotting)
nearest_circles_slider.on_changed(image_reprocessing_plotting)
font_inc_button.on_clicked(increase_font)
font_dec_button.on_clicked(decrease_font)
extract_button.on_clicked(extract)
reload_button.on_clicked(load_new)

# calling the first iteration of the processing and plotting, this call will only be accessed once in the beginning
image_processing_plotting(threshold, specificity, max_detection_size, nearest_circles, scaling, font_size)
