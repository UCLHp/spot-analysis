import datetime
import numpy as np
from scipy import ndimage
import os

import cv2
import easygui as eg
import openpyxl

# additional packages
import pandas as pd
# from math import ceil
from math import sqrt
import copy
import matplotlib.pyplot as plt

# other python scripts
import spot_position_mod as spm
import constants as cs

pred_xrv4000 = cs.pred_xrv4000
pred_xrv3000 = cs.pred_xrv3000

def calc_shifts(df, device):
    ''' calculate
    1.) the x-, y- shift-abs from the absolute plot
    2.) the x-, y- shift-rel from the relative plot'''
    if device == 'XRV-4000':
        nrows = 5
        ncols = 3
        pos = pred_xrv4000


    elif device == 'XRV-3000':
        nrows = 3
        ncols = 3
        pos = pred_xrv3000

    # gradient ratio for the horizontal, vertical, bltr and tlbr profiles
    hor_gr = []
    vert_gr = []
    bltr_gr = []
    tlbr_gr = []

    # absolute shifts
    xs_abs = []
    ys_abs = []

    # relative shifts
    xs_rel = []
    ys_rel = []

    # centre database
    centre = df.loc[df['spot'] == 'Centre']
    centre = centre.set_index('energy')

    for i in df.index:
        e = df.iloc[i, 2]
        p = df.iloc[i, 5]

        cx = centre.loc[e, 'x-pos']
        cy = centre.loc[e, 'y-pos']

        # absolute
        x_abs = df.iloc[i, 6] - pos[p][0]
        y_abs = df.iloc[i, 7] - pos[p][1]

        xs_abs.append(x_abs)
        ys_abs.append(y_abs)

        # relative
        x_rel = df.iloc[i, 6] - cx - pos[p][0]
        y_rel = df.iloc[i, 7] - cy - pos[p][1]

        xs_rel.append(x_rel)
        ys_rel.append(y_rel)

        # gradient ratio of right side to left side
        h = df.iloc[i, 8]/ df.iloc[i, 9] # (right gradient / left gradient)
        v = df.iloc[i, 11]/ df.iloc[i, 12]
        b = df.iloc[i, 14]/ df.iloc[i, 15]
        t = df.iloc[i, 17]/ df.iloc[i, 18]

        hor_gr.append(h)
        vert_gr.append(v)
        bltr_gr.append(b)
        tlbr_gr.append(t)

        # print(f'e:{e} p: {p} x:{x} y:{y}')

    df['x-shift-abs'] = xs_abs
    df['y-shift-abs'] = ys_abs

    df['x-shift-rel'] = xs_rel
    df['y-shift-rel'] = ys_rel

    df['hor_gr'] = hor_gr
    df['vert_gr'] = vert_gr
    df['bltr_gr'] = bltr_gr
    df['tlbr_gr'] = tlbr_gr

    # print(f'df.columns : {df.columns}')


    return df

def rotate_image(array, angle, pivot):
    '''Function to rotate an array CCW a given angle around a defined axis
    inputs:
    array - 2D image structure (numpy array )'''
    # ## Add 0 on both axis such that the pivot is at the centre of the array
    padx = [array.shape[1] - pivot[0], pivot[0]]
    pady = [array.shape[0] - pivot[1], pivot[1]]
    # ## Add padding to array
    array_p = np.pad(array, [pady, padx], 'constant')
    array_r = ndimage.rotate(array_p, angle, reshape=False)
    return array_r[pady[0]:-pady[1], padx[0]:-padx[1]]
    # further info here: https://stackoverflow.com/questions/25458442/rotate-a-2d-image-around-specified-origin-in-python

def spot_to_profiles_old(myimage, activescript):
    '''Extract cartesian and diagonal profiles from spot array'''
    blurred = cv2.GaussianBlur(myimage, (11, 11), 0)
    normed = blurred/blurred.max()

    (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(blurred)

    horprof = [range(len(normed[0])), normed[max_loc[1]]]
    vertprof = [range(len(normed)), [x[max_loc[0]] for x in normed]]
    spin_ccw = rotate_image(normed, 45, max_loc)
    spin_cw = rotate_image(normed, -45, max_loc)
    # ## Top left to bottom right profile
    tl_br = [range(len(spin_ccw[0])), spin_ccw[max_loc[1]]]
    # ## Bottom left to top right profile
    bl_tr = [range(len(spin_cw[0])), spin_cw[max_loc[1]]]
    horprof[0] = [x/activescript.CameraHRatio for x in horprof[0]]
    vertprof[0] = [x/activescript.CameraVRatio for x in vertprof[0]]

    # ## Diagonal profile correction to distance from pixel size uses mean of xy
    diag_ratio = (activescript.CameraHRatio + activescript.CameraVRatio) / 2
    tl_br[0] = [x/diag_ratio for x in tl_br[0]]
    bl_tr[0] = [x/diag_ratio for x in bl_tr[0]]

    return horprof, vertprof, tl_br, bl_tr

def spot_to_profiles(myimage, pixel_loc, activescript):
    ''' steps >> input the spot profile in np.array
        >> apply cv2.GaussianBlur filter to smooth out the profiles
        >> find the max. values in the x (column of the image) and y (row of the image)
        >> store the profile in a nested list [[image coordinates], [values]]'''

    # print(f'myimage.shape : {myimage.shape}')
    blurred = cv2.GaussianBlur(myimage, (11, 11), 0)
    normed = blurred/blurred.max()

    (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(blurred)

    d = int(len(myimage[0])/2)

    # ## horizontal profile
    h_arr = range(len(normed[0]))
    mh = max(normed[max_loc[1]]) # normalised the profile
    horprof = [pixel2mm(h_arr, activescript, 'x'), normed[max_loc[1]], myimage[max_loc[1]]]

    # ## vertical profile
    v_arr = range(len(normed))
    mv = max(normed[max_loc[0]])
    vertprof = [pixel2mm(v_arr, activescript, 'y'), normed[max_loc[0]], myimage[max_loc[0]]]

    # ##  top left to bottom right profile
    tl_arr = range(len(normed))
    ml =  max(normed.diagonal())
    tl_br = [pixel2mm(tl_arr, activescript, 'd'), normed.diagonal(), myimage.diagonal() ]

    # ##  top right to bottom left profile
    tr_arr = range(len(normed))
    mr =  max(np.fliplr(normed).diagonal())
    tr_bl =  [pixel2mm(tr_arr, activescript, 'd'), np.fliplr(normed).diagonal(), np.fliplr(myimage).diagonal()]

    return horprof, vertprof, tl_br, tr_bl

def pixel2mm(pixel_arr, activescript, prof_dir):
    ''' to convert the pixel to image coordinates
    input: pixel_arr (the array for profile)
    activescript : the object from the activescript.txt
    pro_dir =  x (short axis for 4000) || y ( long axis for 4000) || d = diagonal'''


    if activescript.device == '4000':
        if prof_dir == 'x':
            resol = activescript.CameraVRatio
            # npixels = 1200
        elif prof_dir == 'y':
            resol = activescript.CameraHRatio
            # npixels = 1600
        elif prof_dir == 'd':
            resol =  1/sqrt((1/activescript.CameraVRatio)**2+(1/activescript.CameraVRatio)**2)
    elif activescript.device == '3000':
        if prof_dir == 'x':
            resol = activescript.CameraHRatio
            # npixels = 1200
        elif prof_dir == 'y':
            resol = activescript.CameraVRatio
            # npixels = 1200
        elif prof_dir == 'd':
            resol = 1/sqrt((1/activescript.CameraVRatio)**2+(1/activescript.CameraVRatio)**2)

    val = [(p/resol) for p in pixel_arr]

    return val

# ##  ---------------- groups of fetch parameter functions ------------------------
def find_indices(percent, arr_mm, nor_amp,  raw_amp):
    ''' use the indice corresponding to the 0.8/0.2/0.5 normalised amplitude
    ind_l >> index for the left side of the profile
    ind_r >> index for the right side of the profile '''

    nor_p = [i/max(nor_amp.tolist()) for i in nor_amp.tolist()]

    # ## find the index for the centre
    i_centre = nor_p.index(max(nor_p))

    left_prof = nor_p[:i_centre]
    right_prof = nor_p[i_centre:]

    above_percent = [] # find the items that are higher than the percent.
    for i in nor_p:
        if i > float(percent):
            above_percent.append(i)

    ind_l = left_prof.index(above_percent[0])
    ind_r = i_centre + right_prof.index(above_percent[-1])

    return ind_l, ind_r

def interpolate(p, x_arr, y_arr):
    ''' To interpolate p from two points
        p = percent.
        x_arr, y_arr = two items in a list '''

    s = (float(y_arr[1]) - float(y_arr[0]))/(float(x_arr[1]) - float(x_arr[0]))
    c = float(y_arr[1]) - float(s*x_arr[1])

    val = s*p+c

    return val

def interpol_point(percent, ind, arr_mm, nor_amp, raw_amp):
    ''' find the point (x,y) at 0.8/0.2/0.5 using interpolation
        mm : millimeter in image coordinates
        amp :  the profile amplitude in grey scale
        2022-04-12: we decided to use nor_amp (normalised to its max) profile to get all 0.8, 0.2, 0.5 points '''

    # nor_p = [i/max(raw_amp.tolist()) for i in raw_amp.tolist()]
    nor_p = [i/max(nor_amp.tolist()) for i in nor_amp.tolist()]
    i_centre = nor_p.index(max(nor_p))

    if arr_mm[ind] < arr_mm[i_centre] : # left gradient
        if nor_p[ind]>percent:
            arr = [arr_mm[ind-1], arr_mm[ind]]
            nor = [nor_p[ind-1], nor_p[ind]]
            raw = [raw_amp[ind-1], raw_amp[ind]]
        else:
            arr = [arr_mm[ind], arr_mm[ind+1]]
            nor = [nor_p[ind], nor_p[ind+1]]
            raw = [raw_amp[ind], raw_amp[ind+1]]
    else: # right gradient
        if nor_p[ind]>percent:
            arr = [arr_mm[ind], arr_mm[ind+1]]
            nor = [nor_p[ind], nor_p[ind+1]]
            raw = [raw_amp[ind], raw_amp[ind+1]]
        else:
            arr = [arr_mm[ind-1], arr_mm[ind]]
            nor = [nor_p[ind-1], nor_p[ind]]
            raw = [raw_amp[ind-1], raw_amp[ind]]

    # mm = np.interp(percent, nor, arr)
    # amp = np.interp(percent, nor, raw)

    mm = interpolate(percent, nor, arr)
    amp = interpolate(percent, nor, raw)

    return [mm, amp]

def fetch_parameters(arr_mm, nor_amp, raw_amp):
    ''' arr_mm :  convert pixel to mm using the resolution
        nor_amp :  profile from 2d Gaussian filtered spot data (normalised to the spot maximum in a 2d array)
        raw_amp : profile from 2d spot raw data'''



    percent = [0.8, 0.2, 0.5]
    outcome = {key:[[0], [0]] for key in percent}
    for i, p in enumerate(percent):
        ind_l, ind_r = find_indices(p, arr_mm, nor_amp, raw_amp)
        outcome[p][0] = interpol_point(p, ind_l, arr_mm, nor_amp, raw_amp)
        outcome[p][1] = interpol_point(p, ind_r, arr_mm, nor_amp, raw_amp)

    # lgrad = (outcome[0.8][0][1] - outcome[0.2][0][1])/(outcome[0.8][0][0] - outcome[0.2][0][0])
    # rgrad = (outcome[0.8][1][1] - outcome[0.2][1][1])/(outcome[0.8][0][0] - outcome[0.2][1][0])
    lgrad = (80-20)/(outcome[0.8][0][0] - outcome[0.2][0][0])
    rgrad = (80-20)/(outcome[0.8][1][0] - outcome[0.2][1][0])
    fwhm = outcome[0.5][1][0] - outcome[0.5][0][0]

    # -----------------------------------------------------------------------------------
    # # --------------------------debug for gradient ratio-------------------------------
    # -----------------------------------------------------------------------------------
    # deb_r = rgrad/lgrad
    #
    # if deb_r < -1.1 or deb_r > -0.9:
    #
    #     print(f'>>> deb_r :{deb_r}')
    #     print(f'ind_l: {ind_l} , ind_r: {ind_r}')
    #     print(f'outcome: {outcome}')
    #
    #     print(f'nor_amp: {nor_amp}')



    # -----------------------------------------------------------------------------------


    return lgrad, rgrad, fwhm

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

def select_acquisition_info():
    gantry = eg.choicebox('Please select room',
                          'Gantry',
                          ['Gantry 1', 'Gantry 2',
                           'Gantry 3', 'Gantry 4'
                           ]
                          )

    energy = eg.integerbox(msg='Energy',
                           title='Select energy of acquired image',
                           lowerbound=70,
                           upperbound=245
                           )
    gantry_angle = eg.integerbox(msg='Gantry Angle',
                                 title='Select angle of acquisition',
                                 lowerbound=0,
                                 upperbound=360
                                 )
    operators = ['AB', 'AK', 'AGo', 'AGr', 'AM', 'AJP', 'AT', 'AW',
                 'CB', 'CG', 'KC', 'PI', 'SC', 'SG', 'TNC', 'VMA', 'VR']

    operator = eg.choicebox('Select Operator',
                            'Operator',
                            operators
                            )
    return [gantry, energy, gantry_angle, operator]

def write_to_results_wb(results_loc, results):
    wb = openpyxl.load_workbook(results_loc)
    ws = wb.worksheets[0]
    ws.append(results)
    wb.save(results_loc)
