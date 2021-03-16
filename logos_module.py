import os

import numpy as np
import pandas as pd
from scipy.ndimage import median_filter
from PIL import Image
from astropy.modeling import models, fitting


def image_to_array(my_file, norm=False):
    '''Read image data into numpy array

    Takes a file path as an input and reads it using the PIL Image library and
    then returns the data as a numpy array.
    Will normalise the array to a maximum of 1 if norm set to True
    '''
    my_image = Image.open(my_file)  # Image is a class within the PIL library
    my_array = np.array(my_image)
    if norm:
        my_array = np.true_divide(my_array, np.amax(median_filter(my_array, size=2)))
    return my_array


def fetch_output_data(image_dir):
    '''Read LOGOS analysis results of spot from output.txt in same directory

    input: path object or string pertaining to image obtained by logos

    returns: dictionary containing relevant information listed below:
        [Center, FrameRate, Gain, DateTime, Width, RWidth, 2DWidth, Quality]
    '''

    # Get output file location and beam number from input image directory
    output_loc = os.path.join(os.path.dirname(image_dir), 'output.txt')
    image_num = int(os.path.basename(image_dir).split('.')[0])

    # Put full data into list to read out relevant information
    full_data = []
    for line in open(output_loc, 'r'):
        full_data.append([x.lstrip().rstrip() for x in line.split(',')])

    # Create then fill dictionary with relevant information from file
    output_data = {}

    center_index = full_data[0].index('Center XY:')
    output_data['CameraCenter'] = [full_data[0][center_index + 1],
                                   full_data[0][center_index + 2]
                                   ]
    output_data['FrameRate'] = full_data[0][full_data[0].index('FrameRate:')+1]
    output_data['Gain'] = full_data[0][full_data[0].index('Gain:')+1]
    output_data['DateTime'] = full_data[0][full_data[0].index('Time-Date:')+1]

    # Find index for row containing relevant spot information then assign
    irow = [full_data.index(x) for x in full_data if x[0] == str(image_num)][0]
    row = full_data[irow]

    output_data['RelativeCenter'] = [row[row.index('X1Y1Z1')+1],
                                      row[row.index('X1Y1Z1')+2]
                                      ]
    output_data['Width'] = row[row.index('Width')+1]
    output_data['RWidth'] = row[row.index('RWidth')+1]
    output_data['2DWidth'] = row[row.index('2DWidth')+1]
    output_data['Quality'] = row[row.index('Quality')+1]

    return(output_data)


def fetch_pixel_dimensions(image_dir):
    '''Fetch pixel dimensions for spot from activescript.txt file

    input: path object or string pertaining to image obtained by logos

    returns: list [pixels per mm Horizontal, pixels per mm Vertical]
    '''

    # Get active script location from input image directory
    actscr_loc = os.path.join(os.path.dirname(image_dir), 'activescript.txt')

    # Extract pixel dimension data from Active Script file
    for line in open(actscr_loc, 'r'):
        if line.startswith('CameraHRa'):
            CameraHRatio = float(line[15:])
        if line.startswith('CameraVRa'):
            CameraVRatio = float(line[15:])

    return[CameraHRatio, CameraVRatio]


def central_pixel(cameracenter, pixeldimensions, relativecenter):
    '''Find central pixel of image array described by LOGOS'''
    cameracenter = [float(x) for x in cameracenter]
    relativecenter = [float(x) for x in relativecenter]
    x = cameracenter[0] + (pixeldimensions[0] * relativecenter[0])
    y = cameracenter[1] + (pixeldimensions[1] * relativecenter[1])

    return [int(x), int(y)]


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


def raw_profiles(imagearray, center):
    '''Returns X, Y profiles centered on LOGOS defined center

    Inputs
    Image array - the spot tif file as a numpy array
    center - read from LOGOS Output.txt file

    Returns
    list containing horizontal and vertical profiles
    '''
    hor_y = imagearray[center[1]]
    hor_x = [x for x in range(len(imagearray[0]))]
    vert_y = [pixelrow[center[0]] for pixelrow in imagearray]
    vert_x = [x for x in range(len(vert_y))]
    return [hor_x, hor_y, vert_x, vert_y]

def adjusted_profiles(rawprofiles, center, pixeldimensions):
    '''Centers coordinates on central pixel and converts distance from pixels
    to mm

    Inputs
    raw_profiles - list of raw profiles defined above
    center - read from LOGOS Output.txt file

    Returns
    adjusted_profile - centralised profiles with mm for x axes
    '''
    rawprofiles[0] = [x - center[0] for x in rawprofiles[0]]
    rawprofiles[2] = [x - center[1] for x in rawprofiles[2]]

    rawprofiles[0] = [x/pixeldimensions[0] for x in rawprofiles[0]]
    rawprofiles[2] = [x/pixeldimensions[1] for x in rawprofiles[2]]

    return rawprofiles


class Spot:
    '''Represents single spot with details from LOGOS and options to analyse

    Takes the location of the spot TIF image file and associates it with the
    resuts stored in the associated Output file. Methods available to perform
    fits and plots of the data
    '''
    def __init__(self, image_dir, ga=None, rs=None, dist=None, energy=None):
        self.imagearray = image_to_array(image_dir, norm=True)
        self.pixeldimensions = fetch_pixel_dimensions(image_dir)
        self.output_data = fetch_output_data(image_dir)
        self.central_pixel = central_pixel(self.output_data['CameraCenter'],
                                           self.pixeldimensions,
                                           self.output_data['RelativeCenter']
                                           )
        self.rawprofiles = raw_profiles(self.imagearray,
                                        self.central_pixel
                                        )
        self.adjustedprofiles = adjusted_profiles(self.rawprofiles,
                                                  self.central_pixel,
                                                  self.pixeldimensions
                                                  )
        self.ga = ga
        self.rs = rs
        self.dist = dist
        self.energy = energy
        self.singlefit = None
        self.singlefitarray = None
        self.doublefit = None
        self.doublefitarray = None

    def rotate_pixeldata(self, times=1):
        '''Rotate pixel array 90 degrees anticlockwise'''
        for x in range(times):
            self.imagearray = np.rot90(self.imagearray, 1)

    def create_fits(self):
        fit_p = fitting.SLSQPLSQFitter()
        maxpix = np.amax(median_filter(self.imagearray, size=2))
        singl_gaus_mod = models.Gaussian2D(amplitude=maxpix,
                                           x_mean=0,
                                           y_mean=0,
                                           bounds={'amplitude': (0.7 * maxpix, 1.3 * maxpix),
                                                   'theta': (-1.58, 1.58)}
                                           )

        doubl_gaus_mod = doubl_gaus(amplitude=maxpix,
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

        x, y = np.meshgrid(np.arange(0, len(self.imagearray[0])),
                           np.arange(0, len(self.imagearray))
                           )
        x = np.true_divide(x - self.central_pixel[0], self.pixeldimensions[0])
        y = np.true_divide(y - self.central_pixel[1], self.pixeldimensions[1])

        normarray = np.true_divide(self.imagearray, self.imagearray[central_pixel[0]]central_pixel[1])

        print(f'Fitting Single Gaussian for {self.energy}')
        p1 = fit_p(singl_gaus_mod, x, y, median_filter(normarray, size=2), verblevel=0)
        print(f'Fitting Double Gaussian for {self.energy}')
        p2 = fit_p(doubl_gaus_mod, x, y, median_filter(normarray, size=2), verblevel=0)

        self.singlefit = p1
        self.singlefitarray = p1(x,y)
        self.doublefit = p2
        self.doublefitarray = p2(x, y)


def create_location_key(acquisitionlog):
    '''Read acquisitionlog into pandas df and perform light edits'''

    location_key = pd.read_excel(acquisitionlog, engine='openpyxl')
    location_key['Image'] = [str(int(i)).zfill(8) for i in location_key['Image']]
    location_key['Collated Number'] = [str(int(i)).zfill(8) for i in location_key['Collated Number']]

    return(location_key)


def create_spot_dataset(acquisitionlog, acquiredfoldersdir):
    '''Create pandas df with spot output data for spots in acquisitionlog'''

    spot_dataset = create_location_key(acquisitionlog)

    _spot_dataset = [list(spot_dataset.columns)]
    _spot_dataset[0].extend(['Width', 'RWidth', '2DWidth'])

    for index, row in spot_dataset.iterrows():
        print(f'Row {index+1} of {len(spot_dataset)}')
        image_folder = row['Folder']
        image_name = row['Image'] + '.tif'

        src = os.path.join(acquiredfoldersdir, image_folder)

        output_data = fetch_output_data(os.path.join(src, image_name))
        row = list(row)
        row.append(output_data['Width'])
        row.append(output_data['RWidth'])
        row.append(output_data['2DWidth'])
        _spot_dataset.append(row)

    spot_dataset = pd.DataFrame(_spot_dataset[1:], columns=_spot_dataset[0])
    return spot_dataset


# xlsxfile = 'C:\\Users\\csmgi\\Desktop\\Work\\LocalLOGOSAnalysis.xlsx'
# allfoldersdir = 'C:\\Users\\csmgi\\Desktop\\LOGOS Analysis_2'
#
# myspot = Spot(TESTDIR)
# myspot.create_fits()
#
# print(myspot.singlefit)
# print(myspot.doublefit)








def csv_to_array(filename):
    """Return image numpy array of image plus pitch (pixel size)
    """

    spotdata = open(filename).readlines()

    # Image pitch (pixel width) is in first line
    pitch = float(spotdata[0].split("Pitch:,")[1].split(",")[0].strip())

     # 3rd line contains image dimension - ALWAYS??      ##TODO: CHECK CORRECT FOR NON-SQUARE IMAGES
    nrows = int( spotdata[2].split(",")[1].strip() )    # or is this x dim => no. columns?
    ncols = int( spotdata[2].split(",")[2].strip() )    #            y dim => no. rows?

    spotimage = np.zeros( [nrows,ncols] )   ## format np([rows,cols])

    for row in range(3, nrows+3): # Image data starts on fourth row
        spotimage[row-3] = np.array( spotdata[row].split(",") ).astype(float)

    return spotimage  # , pitch


# def find_centre(my_array, *, threshold=0.9,  norm=True):
#     '''
#     Takes a numpy array as input and uses the threshold to make a binary image
#     the upper/lowermost, left/rightmost pixels are used to find center pixel
#     based on a normalised array by default but can use absolute image values
#     '''
#     sub_array = np.copy(my_array)
#     sub_array[0:35] = 0
#     sub_array[1565:] = 0
#     sub_array[:, 0:20] = 0
#     sub_array[:, 1180:] = 0
#     if norm:
#         sub_array = np.true_divide(sub_array, np.amax(sub_array))
#     sub_array = sub_array.astype(np.float)  # np.true_divide(my_array, 1)
#     above_thresh = np.where(sub_array > threshold)
#     CentreRow = int((max(above_thresh[0])+min(above_thresh[0]))/2)
#     CentreCol = int((max(above_thresh[1])+min(above_thresh[1]))/2)
#     return [CentreRow, CentreCol]


def central_xy_profiles(array, center, resolution=[1, 1]):
    '''
    Returns 'x' 'y' profiles of an array at the index defined by 'centre'
    these profiles are centred at 0 and distances are absolute
    '''
    x = np.asarray(range(0, array.shape[1]))
    y = np.asarray(range(0, array.shape[0]))
    centered_x = (x - center[1])/resolution[0]
    centered_y = (y - center[0])/resolution[1]

    XProfile = np.asarray([centered_x, array[center[0]]])
    YProfile = np.asarray([centered_y, array[:, center[1]]])

    return XProfile, YProfile


# def crop_center(img, cropx, cropy):
#     y, x = img.shape
#     startx = x//2-(cropx//2)
#     starty = y//2-(cropy//2)
#     return img[starty:starty+cropy, startx:startx+cropx]

# No longer required as Double Gaussian taken from astropy library with offset



# No longer required as Double Gaussian taken from astropy library with offset



def uniformity_ROI(uniformity_array, threshold=0.5):
    '''Returns central region of rectangular field and image for reference

            Parameters:
                uniformity_array(numpy): greyscale uniformity image as np array
                threshold(float): where to threshold the image to delect ROI

            Returns:
                ROI_display(matplotlib): image to confirm ROI on original image
                uniformity(float): central region uniformity metric
                                   calculated by ~ 100*(max-min)/(max+min)
    '''
    area_above_thresh = np.where(uniformity_array > threshold)

    width = max(area_above_thresh[1]) - min(area_above_thresh[1])
    height = max(area_above_thresh[0]) - min(area_above_thresh[0])

    left80 = int(min(area_above_thresh[0]) + 0.1 * width)
    right80 = int(min(area_above_thresh[0]) + 0.9 * width)
    top80 = int(min(area_above_thresh[1]) + 0.1 * height)
    bottom80 = int(min(area_above_thresh[1]) + 0.9 * height)

    ROI_display = np.copy(uniformity_array)
    ROI_display[top80, left80:right80] = 0
    ROI_display[bottom80, left80:right80] = 0
    ROI_display[top80:bottom80, left80] = 0
    ROI_display[top80:bottom80, right80] = 0

    ROI = uniformity_array[top80:bottom80, left80:right80]
    return ROI, ROI_display

# Functions no longer used.
#
#
#
#
# #######################
# #Collection of functions used in other code for the analysis of spot profiles
# #######################
# from scipy.optimize import curve_fit
#
# def ReadLOGOS(filename):
#     FullFile=list(reader(open(filename)))
#     Pitch = float(FullFile[0][4])
#     Size = int(FullFile[4][2])
#     Data = FullFile[5:(Size+6)]
#     return(FullFile,Data,Pitch)
#
#
# def rotateImage(array, angle, pivot): #Function to rotate an array a given angle around a defined axis
#     padX = [array.shape[1] - pivot[0], pivot[0]] #Creates 0's on the X axis such that the pivot is at the centre of the array
#     padY = [array.shape[0] - pivot[1], pivot[1]] #Creates 0's on the Y axis such that the pivot is at the centre of the array
#     arrayP = np.pad(array, [padY, padX], 'constant') #Adds padding to the array
#     arrayR = ndimage.rotate(arrayP, angle, reshape=False) #Rotates the array around it's centre
#     return arrayR[padY[0] : -padY[1], padX[0] : -padX[1]] #Removes the previously added padding and returns the result
#     #further info here: https://stackoverflow.com/questions/25458442/rotate-a-2d-image-around-specified-origin-in-python
#
#
# def FileNameToSpotPosition(Energyfilename, Params):
#     original = cv2.imread(Energyfilename) # Creates a variable for the image file as an array
#     gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY) # Ensures the image is in grayscale
#     blurred = cv2.GaussianBlur(gray, (51, 51), 0, cv2.BORDER_ISOLATED) # blurring the image is better for the thresholding, 51 is the size of the kernel
#     thresholded = cv2.threshold(blurred, Params['Threshold'].item(), 255, cv2.THRESH_BINARY)[1]
#     eroded = cv2.erode(thresholded, None, iterations=2)
#     dilated = cv2.dilate(eroded, None, iterations=2)
#     circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, Params['Min Distance Between Spots'].item(), param1=50, param2=Params['Specificity'].item(), minRadius=0, maxRadius=int(Params['Max Detection Size'].item()))
#     circles = np.round(circles[0, :]).astype("int")
#     SpotPosns = np.delete(circles,2,axis=1)
#     order = np.round(SpotPosns,decimals=-2)
#     sort=np.lexsort((order[:,0],order[:,1]))
#     SpotPosns = SpotPosns[sort]
#     return(SpotPosns)
