import numpy as np
from scipy import ndimage
import math
import cv2
from csv import reader
#######################
#Collection of functions used in other code for the analysis of spot profiles
#######################
from scipy.optimize import curve_fit

def ReadLOGOS(filename):
    FullFile=list(reader(open(filename)))
    Pitch = float(FullFile[0][4])
    Size = int(FullFile[4][2])
    Data = FullFile[5:(Size+6)]
    return(FullFile,Data,Pitch)

def func(x, a, b, c): # Defines the equation to calculate the double gaussian, a, b, c, d, e and f are the parameters of the fit.
    return (a * np.exp(-((x**2)/(2*b*b)))) + ((1-a) * np.exp(-((x**2)/(2*c*c))))


def FitAndDiff(Profile): # This function optimises the parameters in the above function to best fit the X,Y DataFrame supplied (Profile)

    popt, pcov = curve_fit(func, Profile[0], Profile[1], p0=[0.7, 100, 100], bounds=([0.5,0.001,0.001],[1.,10000.,10000.]))     # "AW" added constraints to the parameters but all I really wanted was for them to be positive
    return popt #Outputs popt which is an array of the parameters.

def rotateImage(array, angle, pivot): #Function to rotate an array a given angle around a defined axis
    padX = [array.shape[1] - pivot[0], pivot[0]] #Creates 0's on the X axis such that the pivot is at the centre of the array
    padY = [array.shape[0] - pivot[1], pivot[1]] #Creates 0's on the Y axis such that the pivot is at the centre of the array
    arrayP = np.pad(array, [padY, padX], 'constant') #Adds padding to the array
    arrayR = ndimage.rotate(arrayP, angle, reshape=False) #Rotates the array around it's centre
    return arrayR[padY[0] : -padY[1], padX[0] : -padX[1]] #Removes the previously added padding and returns the result
    #further info here: https://stackoverflow.com/questions/25458442/rotate-a-2d-image-around-specified-origin-in-python

def funcLOG(x,a,b,c):
    return np.log10((a * np.exp(-((x**2)/(2*b*b)))) + ((1-a) * np.exp(-((x**2)/(2*c*c)))))

def FitAndDiffLOG(Profile): # This function optimises the parameters in the above function to best fit the X,Y DataFrame supplied (Profile)
    popt, pcov = curve_fit(funcLOG, Profile[0], Profile[1], p0=[0.7, 15, 100], bounds=([0.5,0.001,0.001],[1.,1000000.,1000000.]))     # "AW" added constraints to the parameters but all I really wanted was for them to be positive
    return popt #Outputs popt which is an array of the parameters.

def funcLOGShift(x,a,b,c,d):
    return np.log10((a * np.exp(-(((x-b)**2)/(2*c*c)))) + ((1-a) * np.exp(-(((x-b)**2)/(2*d*d)))))

def FitAndDiffLOGShift(Profile): # This function optimises the parameters in the above function to best fit the X,Y DataFrame supplied (Profile)
    popt, pcov = curve_fit(funcLOGShift, Profile[0], Profile[1], p0=[0.7, 0, 15,100], bounds=([0.5,-30,0.001,0.001],[1.,30,1000000.,1000000.]))     # "AW" added constraints to the parameters but all I really wanted was for them to be positive
    return popt #Outputs popt which is an array of the parameters.

def SpotArrayToProfiles(SpotArray,Hor,Vert):
    NData0 = np.true_divide(SpotArray,np.amax(SpotArray))
    itemindex = np.where(NData0>0.90) # Returns an array of the position of all cells greater than 90% - 90 was picked from looking at example data
    CenterRow = int((max(itemindex[0])+min(itemindex[0]))/2) #Finds the row number of the Center of mass of the 90% isodose line
    CenterCol = int((max(itemindex[1])+min(itemindex[1]))/2) #Finds the column number of the Center of mass of the 90% isodose line
    SpotCenter = [CenterRow, CenterCol]
    X = np.asarray(range(0,SpotArray.shape[1])) #Creates list of numbers from 0 to the number of pixels per row
    Y = np.asarray(range(0,SpotArray.shape[0])) #Creates list of numbers from 0 to the number of pixels per column
    CenteredX=(X-CenterCol)/Hor #Creates an X axis that has the Center of the 90% isodose at 0 in pixels
    CenteredY=(Y-CenterRow)/Vert #Creates a Y axis that has the Center of the 90% isodose at 0 in pixels

    XProfile=[CenteredX,NData0[CenterRow]]
    YProfile=[CenteredY,NData0[:,CenterCol]]

    return XProfile, YProfile, SpotCenter

def SpotArrayToEquation(SpotArray,Hor,Vert):
    NData0 = np.true_divide(SpotArray,np.amax(SpotArray))
    itemindex = np.where(NData0>0.90) # Returns an array of the position of all cells greater than 90% - 90 was picked from looking at example data
    CenterRow = int((max(itemindex[0])+min(itemindex[0]))/2) #Finds the row number of the Center of mass of the 90% isodose line
    CenterCol = int((max(itemindex[1])+min(itemindex[1]))/2) #Finds the column number of the Center of mass of the 90% isodose line
    X = np.asarray(range(0,SpotArray.shape[1])) #Creates list of numbers from 0 to the number of pixels per row
    Y = np.asarray(range(0,SpotArray.shape[0])) #Creates list of numbers from 0 to the number of pixels per column
    CenteredX=(X-CenterCol)/Hor #Creates an X axis that has the Center of the 90% isodose at 0 in pixels
    CenteredY=(Y-CenterRow)/Vert #Creates a Y axis that has the Center of the 90% isodose at 0 in pixels

    XProfile=[CenteredX,NData0[CenterRow]]
    YProfile=[CenteredY,NData0[:,CenterCol]]
    LOGXprofile=[CenteredX,np.log10(NData0[CenterRow])]
    LOGYprofile=[CenteredY,np.log10(NData0[:,CenterCol])]

    XProfileL=[CenteredX[0:CenterCol],NData0[CenterRow][0:CenterCol]]
    YProfileL=[CenteredY[0:CenterRow],YProfile[1][0:CenterRow]]
    XLOGprofileL=[CenteredX[0:CenterCol],np.log10(NData0[CenterRow][0:CenterCol])]
    YLOGprofileL=[CenteredY[0:CenterRow],np.log10(YProfile[1][0:CenterRow])]

    XProfileR=[CenteredX[CenterCol:],NData0[CenterRow][CenterCol:]]
    YProfileR=[CenteredY[CenterRow:],YProfile[1][CenterRow:]]
    XLOGprofileR=[CenteredX[CenterCol:],np.log10(NData0[CenterRow][CenterCol:])]
    YLOGprofileR=[CenteredY[CenterRow:],np.log10(YProfile[1][CenterRow:])]

    XpoptLOGshiftL = FitAndDiffLOGShift(XLOGprofileL)
    XpoptLOGshiftR = FitAndDiffLOGShift(XLOGprofileR)
    YpoptLOGshiftL = FitAndDiffLOGShift(YLOGprofileL)
    YpoptLOGshiftR = FitAndDiffLOGShift(YLOGprofileR)
    return XProfile, XpoptLOGshiftL, XpoptLOGshiftR, YProfile, YpoptLOGshiftL, YpoptLOGshiftR

def ReadActiveScriptLOGOS(textfile):
    file = open(textfile,'r')
    FullData=[]
    for line in file:
        FullData.append((line.rstrip().lstrip()))
    CameraHRatio_Index = [i for i, elem in enumerate(FullData) if 'CameraHRatio' in elem]
    CameraHRatio = FullData[CameraHRatio_Index[0]][15:]
    CameraHRatio = float(CameraHRatio)
    CameraVRatio_Index = [i for i, elem in enumerate(FullData) if 'CameraVRatio' in elem]
    CameraVRatio = FullData[CameraVRatio_Index[0]][15:]
    CameraVRatio = float(CameraVRatio)
    return CameraHRatio, CameraVRatio

def FileNameToSpotPosition(Energyfilename, Params):
    original = cv2.imread(Energyfilename) # Creates a variable for the image file as an array
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY) # Ensures the image is in grayscale
    blurred = cv2.GaussianBlur(gray, (51, 51), 0, cv2.BORDER_ISOLATED) # blurring the image is better for the thresholding, 51 is the size of the kernel
    thresholded = cv2.threshold(blurred, Params['Threshold'].item(), 255, cv2.THRESH_BINARY)[1]
    eroded = cv2.erode(thresholded, None, iterations=2)
    dilated = cv2.dilate(eroded, None, iterations=2)
    circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, Params['Min Distance Between Spots'].item(), param1=50, param2=Params['Specificity'].item(), minRadius=0, maxRadius=int(Params['Max Detection Size'].item()))
    circles = np.round(circles[0, :]).astype("int")
    SpotPosns = np.delete(circles,2,axis=1)
    order = np.round(SpotPosns,decimals=-2)
    sort=np.lexsort((order[:,0],order[:,1]))
    SpotPosns = SpotPosns[sort]
    return(SpotPosns)
