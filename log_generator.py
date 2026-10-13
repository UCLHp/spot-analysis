import numpy as np
from openpyxl import Workbook
import PySimpleGUI as sg
import sys
import os

def create_log(collated_no, logos_folder, logos_image, gantry_angle, rangeshifter, distance, energy, save_path):
    '''
    Function to generate an acquisition log that can be read by the plotting code. The attributes of the acquisition
    can be defined by a range of inputs below:

    collated_no:     Collated number is the order where the files would appear if all 36 spots were acquired in the same
                     folder

    logos_folder:    Folder is the name of the folder from Logos; each folder contains the acquisition between starting
                     and stopping the Logos control script

    logos_image:     Image number is the name of the .bmp file from Logos; each file is an image of a spot

    gantry_angle:    The gantry angle when delivering the spots

    rangeshifter:    The rangeshifter insrted when delivering the spots

    distance:        Spot distance from the isocentre; positive values mean closer to the snout, while negative values
                     mean further away from the snout

    energy:          The 36 energies of the spots; ranging from 70-245 MeV with an interval of 5 Mev

    save_path:       File Path of the Results folder

     Return:
        - path to the log
    '''

    # creating an Excel log
    spot_log = Workbook()
    ws = spot_log.active

    # Headers
    ws.append(['Collated Number', 'Folder', 'Image', 'GA', 'RS', 'Distance', 'Energy'])

    ###################################
    # filling in the acquisition info #
    ###################################
    folder_row = 2 # starting on the row after the headers
    for fld, GA, RS, dist in zip(logos_folder, gantry_angle, rangeshifter, distance): # loop for each folder

        # Image Column
        fld_idx = logos_folder.index(fld) # index of the folder list; use to look up the image sublist
        for i, img_no in enumerate(logos_image[fld_idx], start=folder_row):
            ws.cell(row=i, column=3, value=img_no)
        # Folder Column
        for i in range(folder_row, folder_row + len(logos_image[fld_idx])):
            ws.cell(row=i, column=2, value=fld)
        # GA Column
        for i in range(folder_row, folder_row + len(logos_image[fld_idx])):
            ws.cell(row=i, column=4, value=GA)
        # RS Column
        for i in range(folder_row, folder_row + len(logos_image[fld_idx])):
            ws.cell(row=i, column=5, value=RS)
        # Distance Column
        for i in range(folder_row, folder_row + len(logos_image[fld_idx])):
            ws.cell(row=i, column=6, value=dist)

        folder_row = folder_row + len(logos_image[fld_idx]) # increasing the row number for the next folder

    # Energy Column
    for i, MeV in enumerate(energy, start=2): # start from the beginning
        ws.cell(row=i, column=7, value=MeV)

    # Collated Number column
    for i, col_no in enumerate(collated_no, start=2): # start from the beginning
        ws.cell(row=i, column=1, value=col_no)

    ##############
    # saving log #
    ##############
    log_dir = save_path + r'\Spot_Profile_Log.xlsx' # file path of the log
    spot_log.save(log_dir) # saving log

    return log_dir

def file_gui():
    '''
    File GUI that allows you to select the data path containing all the Logos data folders. The GUI also has a dropdown
    menu to select the gantry and will be used to fetch the reference data later.

    Return:
        - Data path of the Logos data
        - Gantry selected
        - String of operator 1
        - String of operator 2
    '''

    # GUI settings
    sg.theme('DarkAmber')
    off = 14

    GANTRY = ["Gantry 1", "Gantry 2", "Gantry 3", "Gantry 4"] # Gantry dropdown options

    file_layout = [
        [sg.Text('Select the acquisition folder:', size=(45, 1))],
        [sg.In(key="datadir"), sg.FolderBrowse()],
        [sg.Text('*make sure the folder ONLY contains the Logos folders!')],
        [sg.Text('', size=(45, 1))],
        [sg.Text('Operator 1:', size=(14, 1)), sg.In(key="op1", size=(5, 1)),
         sg.Text('      Operator 2:', size=(14, 1)), sg.In(key="op2", size=(5, 1))],
        [sg.Text('Select gantry:', size=(off, 1)), sg.Combo(GANTRY, key="gantry", size=(7, 1))],
        [sg.Text('')],
        [sg.Button('Ok'), sg.Button('Cancel')]
    ]
    file_window = sg.Window('Spot Profile QA', file_layout) # create window

    # Launching GUI
    while True:
        event, values = file_window.read()

        # end script when "cancel" was pressed
        if event == 'Cancel':
            sys.exit()

        # unpacking gui info
        acquiredfoldersdir = values['datadir'] # data path
        gantry = values['gantry']
        Op1 = values['op1']
        Op2 = values['op2']

        # proceed with script when "OK" was pressed
        if event == 'Ok':
            break

    file_window.close()

    return acquiredfoldersdir, gantry, Op1, Op2

def info_gui(acquiredfoldersdir):
    '''
    Info GUI that allows you to loop through the list of Logos data folders and assign acquisition info for each folder.
    Results folder will be created after running through all the GUIs.

    INPUT:
        acquiredfoldersdir:     Data path of the Logos data

    Return:
        - Full list of collated numbers for each set of data
        - List of the logos data folders from the file GUI
        - Full list of image numbers corresponding to the .bmp image file name
        - List of gantry angles corresponding to each Logos data folders
        - List of rangeshifters corresponding to each Logos data folders
        - List of distance from isocentre corresponding to each Logos data folders
        - Full list of energies corresponding to each image
        - Data path of the Results folder created
        - List of camera orientation for each set of data
    '''

    # GUI settings
    sg.theme('DarkAmber')
    off = 14

    # acquisition info fields within the GUI
    ENERGIES = "245,240,235,230,225,220,215,210,205,200,195,190,185,180,175,170,165,160,155,150,145,140,135,130,125,120,115,110,105,100,95,90,85,80,75,70" # default 36 energies
    GANTRY_ANGLE = [0, 90, 180, 270] # dropdown box for GA
    RANGESHIFTER = [0, 2, 3, 5] # dropdown box for RS
    DISTANCE = [40, 20, 10, 0, -10, -20, -40] # dropdown box for dist
    CAMERA_ORIENTATION = ["A", "B", "G", "T"]

    # creating a list of Logos data folders from the data path
    folders = [name for name in os.listdir(acquiredfoldersdir) if os.path.isdir(os.path.join(acquiredfoldersdir, name))]

    # empty list to bin the acquisition info
    image = []
    eng = []
    GA = []
    RS = []
    dist = []
    CamOrient = []

    # loop GUI for each Logos data folders
    for index, i in enumerate(folders):

        info_layout = [
            [sg.Text('Acquisition info for:', size=(0, 1)),sg.Text(i, size=(20, 1))],
            [sg.Text('')],
            [sg.Text('Energies (MeV)', size=(off, 1)), sg.Multiline(ENERGIES, key="energies", size=(50, 3))],
            [sg.Text('', size=(off,1)),sg.Text('*make sure the energies are separated by commas!')],
            [sg.Text('Gantry Angle:', size=(off, 1)), sg.Combo(GANTRY_ANGLE, key="GA", default_value=GANTRY_ANGLE[0], size=(5,1))],
            [sg.Text('Rangeshifter:', size=(off, 1)),sg.Combo(RANGESHIFTER, key="RS", default_value=RANGESHIFTER[0], size=(5,1))],
            [sg.Text('Distance:', size=(off, 1)), sg.Combo(DISTANCE, key="dist", default_value=DISTANCE[3], size=(5,1)),
             sg.Text('*positive values = closer to the snout', size=(off*3, 1))],
            [sg.Text('Camera Orientation:', size=(off, 1)),
             sg.Combo(CAMERA_ORIENTATION, key="cam", default_value=CAMERA_ORIENTATION[3], size=(5, 1))],
            [sg.Text('')],
            [sg.Button('Ok'), sg.Button('Cancel')]
        ]
        info_window = sg.Window('Spot Profile QA', info_layout) # create window

        while True:
            event, values = info_window.read()

            # end script when "cancel" was pressed
            if event == 'Cancel':
                sys.exit()

            # unpacking gui info
            GA.append(values['GA']) # gantry angles
            RS.append(values['RS']) # rangeshifter used
            dist.append(values['dist']) # distance from isocentre
            eng.append([int(x) for x in values['energies'].split(",")]) # turning energies input from str to a list and bin it as a list inside a list
            energy = [i for sublist in eng for i in sublist] # collapse the energy into 1 list that is the same length as the log
            CamOrient.append(values['cam']) # camera orientation

            # Setting image number according to the no. of spots per folder
            image.append(np.linspace(1, len(eng[index]), len(eng[index]))) # setting image no. for each folder from 1 to x, where x is the no. of spots

            # proceed with script when "OK" was pressed
            if event == 'Ok':
                break

        # setting collated number according to the energy range
        data_set = [GA,RS,dist] # sets of data
        col_no = list( np.linspace(1,len(eng[0]),len(eng[0])) )# initial collated numbers from the first set of data

        for i in range(1,len(data_set[0])): # looping from the 2nd set of data to check
            current = [data_set[0][i], data_set[1][i], data_set[2][i]]
            previous = [data_set[0][i-1], data_set[1][i-1], data_set[2][i-1]]

            if current == previous:
                col_no.extend( list(np.linspace(max(col_no) + 1, max(col_no) + len(eng[i]),len(eng[i]))) )
            else:
                col_no.extend( list(np.linspace(1,len(eng[i]),len(eng[i]))) )

        info_window.close()

    # creating results folder
    save_path = os.path.join(acquiredfoldersdir, "Results")
    os.mkdir(save_path)
    print("Results folder created.")  # code status message

    return col_no, folders, image, GA, RS, dist, energy, save_path, CamOrient