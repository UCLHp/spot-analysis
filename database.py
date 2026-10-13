import pypyodbc
import pandas as pd
import PySimpleGUI as sg

import os
from datetime import datetime

def test_db_connection():
    """
    Function to test the connection to Access database. A GUI window will pop up to indicate whether the connection has
    been established. If yes, user can choose whether to write data to the DB.

    Return:
        - String to indicate whether script should write to DB or not
    """
    # GUI settings
    sg.theme('DarkAmber')

    # Data path to the Access database
    #path = r"\\10.140.79.12\rtp-share$\protons\Work in Progress\Xu\Database\AssetsDatabaseInProgressXZ.accdb"  # Dummy DB
    path = r"\\9.40.120.20\RTAssetBE\AssetsDatabase_be.accdb"
    password = ""

    conn = None
    try:
        conn = pypyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s; PWD=%s' % (path, password))
        # GUI window if connection is successful
        file_layout = [
            [sg.Text('Connection to the database is successful!', size=(45, 1))],
            [sg.Text('Please check the graphs!', size=(45, 1))],
            [sg.Text('', size=(45, 1))],
            [sg.Text('Do you want to write data to the database?', size=(45, 1))],
            [sg.Text('', size=(45, 1))],
            [sg.Button('Yes'), sg.Button('No')]
        ]
        file_window = sg.Window('Database Connection', file_layout)  # create window

    except:
        # GUI window if connection is unsuccessful
        file_layout = [
            [sg.Text('WARNING: Database connection is unsuccessful!', size=(45, 1))],
            [sg.Text('Data cannot be written!', size=(45, 1))],
            [sg.Text('', size=(45, 1))],
            [sg.Button('Ok')]
        ]
        file_window = sg.Window('Database Connection', file_layout)  # create window

    # Launching GUI
    while True:
        event, values = file_window.read()

        # proceed with script when "Yes" is pressed
        if event == 'Yes':
            db_write = 'Yes'
            break

        # end script when "No" or "Ok" is pressed
        if event == 'No' or 'Ok':
            db_write = 'No'
            print("Nothing is written to the DB!")
            print("")
            break

    file_window.close()

    return db_write

def write_to_session(conn, acquiredfoldersdir, gantry, CamOrient, Op1, Op2):
    """
    Function to fetch and write data to the SpotProfSession table in the database. The following inputs are needed to
    fetch and write the info:

    conn:                   Connection to the database using pypyodbc

    acquiredfoldersdir:     The directory path of the Logos acquisition folders. The path is used to fetch the datetime
                            of each acquisition and setup info such as equipment used, gantry angle, rangeshifter used
                            and distance from isocentre

    gantry:                 The gantry where the measurement was made. Selected in the file GUI

    CamOrient:              The direction the camera is putting towards: panel A, panel B, gantry or table. Selected in
                            the info GUI for each set of measurements

    Op1:                    Operator 1 of the measurement. Selected in the file GUI

    Op2:                    Operator 2 of the measurement. Selected in the file GUI
    """
    # reading the acquisition Excel log
    save_path = os.path.join(acquiredfoldersdir, "Results")
    LogExcel = os.path.join(save_path, "Spot_Profile_Log.xlsx")
    log = pd.read_excel(LogExcel)
    log_trimmed = log.drop_duplicates(subset=["GA", "RS", "Distance"], keep="last") # trim log down to 1 spot per set

    #################
    # Fetching data #
    #################
    # Reducing the camera orientation list to match the number of session
    folder_lastspot = log_trimmed["Folder"].tolist()  # list of folders with the last spot in each set
    folder_all = log.drop_duplicates(subset=["Folder"], keep="last")["Folder"].tolist() # full list of folders
    miss_idx = [i for i, val in enumerate(folder_all) if val not in folder_lastspot] # index of folders not present in the last spot folder list
    CamOrient = [a for i, a in enumerate(CamOrient) if i not in miss_idx] # reducing camera oientation list according to the missing index

    # looping each row of the log and fetching info for the DB
    for index, row in log_trimmed.iterrows():
        ## info directly from the log ##
        GA = row["GA"] # GA field
        RS = row["RS"] # RS field
        dist = row["Distance"] # Dist field

        ## info from txt ##
        folder = row["Folder"] # logos folder containing the measured spots

        # reading output.txt for datetime
        outputfile = os.path.join(acquiredfoldersdir, folder, "output.txt")
        with open(outputfile, "r") as f:
            lines = f.readlines()
            dt_str = lines[-1][5:24]  # fetching datetime string from the last line
            dt = datetime.strptime(dt_str, "%H:%M:%S %m/%d/%Y") # Adate field

        # reading activescript.txt for equipment used
        actscr_loc = os.path.join(acquiredfoldersdir, folder, 'activescript.txt')
        for line in open(actscr_loc, 'r'):
            # reading the line in the text file indicating what equipment was used
            if line.startswith('TextPath'):
                if '3' in line:
                    equip = 'XRV3000'
                if '4' in line:
                    equip = 'XRV4000'

        ## info from funtion input ##
        camera = CamOrient[0]
        CamOrient = CamOrient[1:] # reduce Camera Orientation list for next iteration

        ###################
        # SpotProfSession #
        ###################
        # empty list to fill a row of session info
        write_session = []
        # writing session info to the list
        write_session.append(dt.strftime('%d/%m/%Y %H:%M:%S')) # datetime format change for Access compatibility
        write_session.append(gantry)
        write_session.append(GA)
        write_session.append(RS)
        write_session.append(dist)
        write_session.append(equip)
        write_session.append(camera)
        write_session.append(Op1)
        write_session.append(Op2)

        # sql request
        session_tb = "SpotProfSession"
        cursor = conn.cursor()
        sql = '''
                INSERT INTO [%s] (ADate, MachineName, GA, RS, Dist, Equipment, CamOrientation, Op1, Op2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
              ''' % session_tb
        cursor.execute(sql, write_session) # writing the session info list to the DB
        conn.commit()


def write_to_data(conn, acquiredfoldersdir,gantry):
    """
    Function to fetch and write data to the SpotProfData table in the database. The following inputs are needed to
    fetch and write the info:

    conn:                   Connection to the database using pypyodbc

    acquiredfoldersdir:     The directory path of the Logos acquisition folders. The path is used to fetch the datetime
                            of each acquisition and setup info such as equipment used, gantry angle, rangeshifter used
                            and distance from isocentre

                            The directory path will also be used to locate the Fit Excel files and fetch the x and y
                            sigma of the fitted spots

    gantry:                 The gantry where the measurement was made. Selected in the file GUI
    """
    # reading the acquisition Excel log
    save_path = os.path.join(acquiredfoldersdir, "Results")
    LogExcel = os.path.join(save_path, "Spot_Profile_Log.xlsx")
    log = pd.read_excel(LogExcel)

    ########################
    # Initial code message #
    ########################
    print("Writing for:") # code status message
    # Initial acquisition info
    last_GA = log["GA"][0]
    last_RS = log["RS"][0]
    last_dist = log["Distance"][0]
    last_files = f"Fits_GA{last_GA}_RS{last_RS}_Dist{last_dist}.xlsx" # initial Excel file
    print(last_files)  # code status message

    #################
    # Fetching data #
    #################
    # list of folder for loop
    log_set = log.drop_duplicates(subset=["GA", "RS", "Distance"], keep="last") # trim log down to last spot per set
    folder = log_set["Folder"].tolist()  # list of folder with the last spot in each set

    # looping each row of the log and fetching info for the DB
    for index, row in log.iterrows():
        ## info directly from the log ##
        GA = row["GA"] # GA field
        RS = row["RS"] # RS field
        dist = row["Distance"] # Dist field
        energy = row["Energy"] # Energy field

        ## info from the fit Excel file ##
        files = f"Fits_GA{GA}_RS{RS}_Dist{dist}.xlsx" # Reading Excel file according to the acquisition info
        FitExcel = os.path.join(save_path, files)

        # reading the fit Excel
        df = pd.read_excel(FitExcel, header=2)
        # fetching x and y sigma according to energy
        data_row = df[df["Energy"] == energy]
        x_sigma = data_row["x_stddev"].iloc[0] # x-sigma field
        y_sigma = data_row["y_stddev"].iloc[0] # y-sigma field

        ######################
        # Excel file checker #
        ######################
        if files != last_files: # check whether the Excel file has changed
            print(files) # code status message
            folder = folder[1:] # shortening the folder list when the Excel file changed
        last_files = files # set file for the next iteration

        ## info from txt ##
        # [The same set can be contained in different folders, code here ensure the latest datetime is fetched]
        # reading output.txt file for datetime
        outputfile = os.path.join(acquiredfoldersdir, folder[0], "output.txt")
        with open(outputfile, "r") as f:
            lines = f.readlines()
            dt_str = lines[-1][5:24]  # fetching datetime string from the last line
            dt = datetime.strptime(dt_str, "%H:%M:%S %m/%d/%Y") # Adate field

        ################
        # SpotProfData #
        ################
        # empty list to fill a row of data info
        write_data = []
        # writing data info to the list
        write_data.append(dt.strftime('%d/%m/%Y %H:%M:%S')) # datetime format change for Access compatibility
        write_data.append(gantry)
        write_data.append(GA)
        write_data.append(RS)
        write_data.append(dist)
        write_data.append(energy)
        write_data.append(x_sigma)
        write_data.append(y_sigma)

        data_tb = "SpotProfData"
        cursor = conn.cursor()
        sql = '''
                INSERT INTO [%s] (ADate, MachineName, GA, RS, Dist, Energy, [x-sigma], [y-sigma])
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
              ''' % data_tb

        cursor.execute(sql, write_data) # writing the data info list to the DB
        conn.commit()

def write_to_db(acquiredfoldersdir, gantry, CamOrient, Op1, Op2):
    """
    Function to connect to the Access database and execute the write_to_session() and write_to_data() functions. Inputs
    of this function are just the inputs required by the write_to functions:

    acquiredfoldersdir:     Needed for write_to_session() and write_to_data()

    gantry:                 Needed for write_to_session() and write_to_data()

    CamOrient:              Only needed for write_to_data()

    Op1:                    Only needed for write_to_data()

    Op2:                    Only needed for write_to_data()
    """
    # Data path and password to the Access database
    #path = r"\\10.140.79.12\rtp-share$\protons\Work in Progress\Xu\Database\AssetsDatabaseInProgressXZ.accdb"   # Dummy DB
    path = r"\\9.40.120.20\RTAssetBE\AssetsDatabase_be.accdb"
    password = ""
    # Establish connection to the DB
    conn = pypyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s; PWD=%s' % (path, password))

    # executing the write_to functions
    print("Writing data to the SpotProfSession table......")
    write_to_session(conn, acquiredfoldersdir, gantry, CamOrient, Op1, Op2)

    print("Writing data to the SpotProfData table......")
    print("")
    write_to_data(conn, acquiredfoldersdir, gantry)
    print("")