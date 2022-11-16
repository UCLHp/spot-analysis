import pandas as pd
import os
import numpy as np
import easygui as eg
import datetime


import matplotlib.pyplot as plt
import PySimpleGUI as sg

import figures as fg
import spot_position_mod as spm
import spot_position_func as spf
import database as db
import constants as cs
import report as rp



gantries = cs.gantries
DATABASE_DIR = cs.DATABASE_DIR
PWD = cs.PWD
db_cols = cs.db_cols

# find gradient radio png
current_path = os.getcwd()
files = os.listdir(current_path)

if 'def_gradient_ratio.png' in files and 'profiles_per_spot.png' in files :
    gr_path = os.path.join(current_path, 'def_gradient_ratio.png')
    prof_path  = os.path.join(current_path, 'profiles_per_spot.png')

else:
    sg.popup('Important!', 'Cannot find the def_gradient_ratio.png or profiles_per_spot.png! Your report may miss something! ')
    prof_path = []
    gr_path  = []


def make_window(theme):
    sg.theme(theme)
    pbt = db.fetch_db(DATABASE_DIR, 'Operators', 'Initials', PWD = PWD)

    if pbt == False:
        eg.msgbox("Unable to fetch operators from database, "
                  "list may not be up to date.")
        operators = cs.operators
    else:
        operators = pbt

    print(f'operators: {operators}')

    # warning = [sg.Text('Operator 2 is required when Operator 1 cannot sign off the spot grid QA.')]
    person_1 = [sg.Text('Operator 1: '), sg.Combo(values= operators, key = '-PERSON1-')]
    person_2 = [sg.Text('Operator 2: '), sg.Combo(values= operators, key = '-PERSON2-')]
    # warning = [sg.Frame('Reminder: ', [[sg.Text('Operator 2 is required when Operator 1 cannot sign off the spot grid QA.')], person_1 + person_2])]
    gantry = [sg.Text('Gantry: '), sg.Combo(values = gantries, key = '-GANTRY-')]
    gantry_angle = [sg.Text('Gantry angle: '), sg.InputText(size = (5, 1), key = '-GANTRY_ANGLE-')]
    col_titles = [sg.Text('Proton energy (MeV)', size = (15, 1), justification = 'l'), sg.Text('Bmp picture locations', size = (20, 1), justification = 'l')]
    ent1 = [sg.Text('(1)'), sg.InputText(size = (10, 1), key = '-PRO_EN_1-', default_text = '70'), sg.Text('@'), sg.InputText(key = '-BMP_LOC_1-'), sg.FileBrowse()]
    ent2 = [sg.Text('(2)'), sg.InputText(size = (10, 1), key = '-PRO_EN_2-', default_text = '100'), sg.Text('@'), sg.InputText(key = '-BMP_LOC_2-'), sg.FileBrowse()]
    ent3 = [sg.Text('(3)'), sg.InputText(size = (10, 1), key = '-PRO_EN_3-', default_text = '150'), sg.Text('@'), sg.InputText(key = '-BMP_LOC_3-'), sg.FileBrowse()]
    ent4 = [sg.Text('(4)'), sg.InputText(size = (10, 1), key = '-PRO_EN_4-', default_text = '200'), sg.Text('@'), sg.InputText(key = '-BMP_LOC_4-'), sg.FileBrowse()]
    ent5 = [sg.Text('(5)'), sg.InputText(size = (10, 1), key = '-PRO_EN_5-', default_text = '240'), sg.Text('@'), sg.InputText(key = '-BMP_LOC_5-'), sg.FileBrowse()]
    comment = [sg.Text('Comments: '), sg.InputText(size = (50, 1), key = '-COMMENT-')]
    button_submit = [sg.Button('Submit')]
    button_exit = [sg.Button('Exit')]


    layout = [[sg.Frame('Reminder: ', [[sg.Text('Operator 2 is required when Operator 1 cannot sign off the spot grid QA.')], person_1 + person_2], size = (550,80))],
             [sg.Frame('Your spot measurements: ', [gantry + gantry_angle, col_titles, ent1, ent2, ent3, ent4, ent5, comment, button_submit + button_exit], size = (550,308))
                ]]

    window = sg.Window('please tell me about your spot measurements:', layout, finalize =True)

    return window

def make_window_after_reviewing_data(theme):
    sg.theme(theme)
    text = [sg.Text('Please review your spot position data! If you have any comments, please write down below.')]
    comment2 = [sg.Text('Comments: '), sg.InputText(size = (50, 1), key = '-COMMENT2-')]

    text1 = [sg.Text('Press SUBMIT to push the data to the proton database!')]

    # buttons
    button_submit = [sg.Button('Submit')]
    button_cancel = [sg.Button('Cancel')]

    # layout = [ text, comment2, button_submit + button_cancel]

    layout = [[sg.Frame('IMPORTANT', [text, comment2], size = (550, 80))],
              [sg.Frame('Data to database', [text1, button_submit + button_cancel], size = (550,80))]]

    window = sg.Window('Data reviewing:' , layout, finalize = True)

    return window

def session_result(gui_values, values2,  spotpatterns):
    ''' gui_values: a dict containing the output of the PySimpleGUI
        spotpatterns: a dict containing the SpotPattern object corresponding to the proton energy'''
    # get the latest measurement date and time from five measurements
    adate = db.get_mea_time(spotpatterns)
    # adate = spotpatterns['240'].output.datetime
    machine_name = 'Gantry ' + gui_values['-GANTRY-']
    # session = 1234
    device = 'XRV-' + spotpatterns['240'].output.device
    operator1 = gui_values['-PERSON1-']
    operator2 = gui_values['-PERSON2-']
    gantry_angle = gui_values['-GANTRY_ANGLE-']
    comment = gui_values['-COMMENT-'] + ' ' + values2['-COMMENT2-']

    # SpotPositionSession (8 entries)
    result = [adate, machine_name, device, gantry_angle, operator1, operator2, comment, None]
    # SpotPositionSession (7 entries)
    # result = [adate, machine_name, device, operator1, operator2, comment, None]
    # print(f'result: {result}')

    # push the session result to the session table in the ASSESS Database
    push_result = db.push_session_data(DATABASE_DIR, result)

    print(f'push_result: {push_result}')
    return push_result

def spot_data(gui_values, spotpatterns):
    ''' To create a nested list, each list contains the physical parameters of a profile of a spot.
        gui_values: a dict containing the output of the PySimpleGUI
        spotpatterns: a dict containing the SpotPattern object corresponding to the proton energy'''

    # get the latest measurement date and time from five measurements
    adate = db.get_mea_time(spotpatterns)

    machine_name = 'Gantry ' + gui_values['-GANTRY-']
    gantry_angle = gui_values['-GANTRY_ANGLE-']

    en =  sorted([int(key) for key in spotpatterns.keys()], reverse = True)
    all_data = {}

    # debug abnormal gradient ratio
    abn_gr = []

    for e in en:
        mea_spot_loc = spotpatterns[str(e)].spots_info
        device = 'XRV-' + spotpatterns[str(e)].output.device
        mloc = spotpatterns[str(e)].mloc
        spot = spotpatterns[str(e)].spot
        loc_names = list(mea_spot_loc.keys()) # list of spot position name corresponding to the spot grid



        # create an empty nested list to store the spot data
        spot_results = [[] for i in range(0, len(loc_names))]

        for i, loc in enumerate(loc_names):
            # add date, gantry, energy, device, gantry angle, loc_name
            spot_results[i].extend([adate, machine_name, int(e),  device, int(gantry_angle), loc])

            # add measured x,y coordinate of the spot (name = loc)
            spot_results[i].extend([mloc[loc][0], mloc[loc][1]])

            # add the rgrad, lgrad, fwhm of the horizontal profiles
            spot_results[i].extend([spot[loc].horprof.rgrad, spot[loc].horprof.lgrad, spot[loc].horprof.fwhm] )
            rh = spot[loc].horprof.rgrad /spot[loc].horprof.lgrad

            # add the rgrad, lgrad, fwhm of the vertical profiles
            spot_results[i].extend([spot[loc].vertprof.rgrad, spot[loc].vertprof.lgrad, spot[loc].vertprof.fwhm] )
            rv = spot[loc].vertprof.rgrad /spot[loc].vertprof.lgrad

            # add the rgrad, lgrad, fwhm of the bltr profiles
            spot_results[i].extend([spot[loc].bl_tr.rgrad, spot[loc].bl_tr.lgrad, spot[loc].bl_tr.fwhm] )
            rbl = spot[loc].bl_tr.rgrad /spot[loc].bl_tr.lgrad

            # add the rgrad, lgrad, fwhm of the tl_br profiles
            spot_results[i].extend([spot[loc].tl_br.rgrad,  spot[loc].tl_br.lgrad,  spot[loc].tl_br.fwhm] )
            rtl = spot[loc].tl_br.rgrad /spot[loc].tl_br.lgrad

            # -----------------------------------------------------------------------------------
            # # --------------------------debugging for gradiet ratio----------------------------
            # -----------------------------------------------------------------------------------
            # gr = [rh, rv, rbl, rtl]
            # profile_name = ['horprof','vertprof','bl_tr','tl_br']
            # for i, r in enumerate(gr):
            #     if r > -0.9 or r < -1.1:
            #         if profile_name[i] == 'horprof':
            #             profile_obj = spot[loc].horprof_p
            #         elif profile_name[i] == 'vertprof':
            #             profile_obj = spot[loc].vertprof_p
            #         elif profile_name[i] == 'bl_tr':
            #             profile_obj = spot[loc].bl_tr_p
            #         elif profile_name[i] == 'tl_br':
            #             profile_obj = spot[loc].tl_br_p
            #         abn_gr.extend([[e, loc, profile_name[i] +'_mm', profile_obj[0]], [e, loc, profile_name[i] + '_nor', profile_obj[1].tolist()], [e, loc, profile_name[i] + '_amp', profile_obj[2].tolist()]])
            # -----------------------------------------------------------------------------------
        all_data.update({e: spot_results})

    # -----------------------------------------------------------------------------------
    # # --------------------------debugging for gradiet ratio----------------------------
    # -----------------------------------------------------------------------------------
    # if abn_gr:
    #     # print(f'abn_gr : {abn_gr}')
    #     df = pd.DataFrame(abn_gr)
    #     df.to_excel('agr_profile.xlsx')

    # -----------------------------------------------------------------------------------

    return all_data, device

def main():
    theme = 'DefaultNoMoreNagging'
    window = make_window(theme)

    while True:
        event, values = window.read() #comment off to test
        # print(f'event = {event}')

# -----------------------------------------------------------------------------------
# # ------------------------------------ debug---------------------------------------
# -----------------------------------------------------------------------------------
        # event = 'Submit' # uncomment to test
        # values = {'-PERSON1-': 'AGr', '-PERSON2-': '', '-GANTRY-': '4', '-GANTRY_ANGLE-': '0', '-PRO_EN_1-': '70', '-BMP_LOC_1-': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0001/00000001.bmp', 'Browse': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0001/00000001.bmp', '-PRO_EN_2-': '100', '-BMP_LOC_2-': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0002/00000001.bmp', 'Browse0': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0002/00000001.bmp', '-PRO_EN_3-': '150', '-BMP_LOC_3-': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0003/00000001.bmp', 'Browse1': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0003/00000001.bmp', '-PRO_EN_4-': '200', '-BMP_LOC_4-': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0004/00000001.bmp', 'Browse2': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0004/00000001.bmp', '-PRO_EN_5-': '240', '-BMP_LOC_5-': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0005/00000001.bmp', 'Browse3': 'C:/Users/KAWCHUNG/Desktop/Spot grids with holder and plan/2022_0525_0005/00000001.bmp', '-COMMENT-': ''}
        # values = {'-PERSON1-': 'KC', '-PERSON2-': '', '-GANTRY-': '3', '-GANTRY_ANGLE-': '0', '-PRO_EN_1-': '70', '-BMP_LOC_1-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0006_70/00000001.bmp', 'Browse': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0006_70/00000001.bmp', '-PRO_EN_2-': '100', '-BMP_LOC_2-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0007_100/00000001.bmp', 'Browse0': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0007_100/00000001.bmp', '-PRO_EN_3-': '150', '-BMP_LOC_3-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0008_150/00000001.bmp', 'Browse1': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0008_150/00000001.bmp', '-PRO_EN_4-': '200', '-BMP_LOC_4-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0009_200/00000001.bmp', 'Browse2': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0009_200/00000001.bmp', '-PRO_EN_5-': '240', '-BMP_LOC_5-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0010_240/00000001.bmp', 'Browse3': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0010_240/00000001.bmp', '-COMMENT-': ''}
        # # home
        # values= {'-PERSON1-': 'KC', '-PERSON2-': '', '-GANTRY-': '4', '-GANTRY_ANGLE-': '0', '-PRO_EN_1-': '70', '-BMP_LOC_1-': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0006_70/00000001.bmp', 'Browse': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0006_70/00000001.bmp', '-PRO_EN_2-': '100', '-BMP_LOC_2-': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0007_100/00000001.bmp', 'Browse0': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0007_100/00000001.bmp', '-PRO_EN_3-': '150', '-BMP_LOC_3-': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0008_150/00000001.bmp', 'Browse1': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0008_150/00000001.bmp', '-PRO_EN_4-': '200', '-BMP_LOC_4-': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0009_200/00000001.bmp', 'Browse2': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0009_200/00000001.bmp', '-PRO_EN_5-': '240', '-BMP_LOC_5-': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0010_240/00000001.bmp', 'Browse3': 'D:/OneDrive - NHS/python_code/spot-analysis/miscellaneous/testing_dataset/2022_03_03_zero2_G3/2022_0303_0010_240/00000001.bmp', '-COMMENT-': ''}

        # values = {'-PERSON1-': 'CG', '-PERSON2-': '', '-GANTRY-': '3', '-GANTRY_ANGLE-': '0', '-PRO_EN_1-': '70', '-BMP_LOC_1-': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0001/00000001.bmp', 'Browse': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0001/00000001.bmp', '-PRO_EN_2-': '100', '-BMP_LOC_2-': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0002/00000001.bmp', 'Browse0': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0002/00000001.bmp', '-PRO_EN_3-': '150', '-BMP_LOC_3-': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0003/00000001.bmp', 'Browse1': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0003/00000001.bmp', '-PRO_EN_4-': '200', '-BMP_LOC_4-': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0004/00000001.bmp', 'Browse2': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0004/00000001.bmp', '-PRO_EN_5-': '240', '-BMP_LOC_5-': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0005/00000001.bmp', 'Browse3': 'T:/Routine QA/Spot Position/Acquired_Folders/Gantry 3/GA0 only (usually 4000 data)/2022_08_29_post_ISM_CG/2022_0829_0005/00000001.bmp', '-COMMENT-': 'post ISM'}
        print(f'values: {values}')
# -----------------------------------------------------------------------------------
# # ------------------------------------ debug---------------------------------------
# -----------------------------------------------------------------------------------
        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            raise SystemExit

        # ## get all gui entries report
        p1 = values['-PERSON1-']
        p2 = values['-PERSON2-']

        # ## reject duplicated operators or empty operator 1
        try:
            # ## reject duplicated operators or empty operator 1
            if values['-PERSON1-'] == values['-PERSON2-']:
                sg.popup('ERROR MESSAGE!','operator 1 and 2 are the same! please entre the correct operators!')
                continue

            if values['-PERSON1-'] == '':
                sg.popup('ERROR MESSAGE!','operator 1 is empty!')
                continue
        except:
            print(f'please check your entry on the gui')

        # #>> check gantry
        try:
            if values['-GANTRY-'] not in ['1', '2', '3', '4'] or values['-GANTRY-'] == '':
                sg.popup('ERROR MESSAGE!', f'please check your gantry entry :)')
                continue

            # #>> check gantry angle
            if values['-GANTRY_ANGLE-'] == "":
                sg.popup('ERROR MESSAGE!', f'please check your gantry angle entry :)')
                continue
        except:
            print(f'please check your entry on the gui')

        # ## reject  empty bmp locations

        kv = list(values.keys())
        vv = list(values.values())
        abmp = [] # all bmp locs
        rbmp = [] # recorded bmp
        dEn = [] # duplicated energy
        mEn = [] # missing energy
        aEn = [] # all energies
        nbmp = 0 # total no of bmp entries on gui

        # ## if we don't allow empty bmp
        # for i, v in enumerate(kv):
        #     if '-BMP_LOC' in v:
        #         nbmp = nbmp+1
        #         me = f'-PRO_EN_{str(nbmp)}-'
        #         mb = f'-BMP_LOC_{str(nbmp)}-'
        #         if values[mb] == "":
        #             mEn.append(values[me])
        #         else:
        #             abmp.append(values[mb])
        #             if abmp.count(values[mb]) >1:
        #                 en_n = [i+1 for i, x in enumerate(abmp) if x == values[mb]] # find the -PRO_EN_n- for duplicated energies
        #                 for n in en_n:
        #                     de = f'-PRO_EN_{str(n)}-'
        #                     dEn.append(values[de])

    # ## if we allow empty bmp
        for i, v in enumerate(kv):
                if '-BMP_LOC' in v:
                    nbmp = nbmp+1
                    me = f'-PRO_EN_{str(nbmp)}-'
                    mb = f'-BMP_LOC_{str(nbmp)}-'
                    aEn.append(values[me])
                    if values[mb] != "":
                        rbmp.append(nbmp)
                        abmp.append(values[mb])
                        if abmp.count(values[mb]) >1:
                            en_n = [i+1 for i, x in enumerate(abmp) if x == values[mb]] # find the -PRO_EN_n- for duplicated energies
                            for n in en_n:
                                de = f'-PRO_EN_{str(n)}-'
                                dEn.append(values[de])


        # # count the number of bmps from the gui ## CG evaluation
        # nbmp = 0
        # for k in values.keys():
        #     if 'BMP_LOC' in k:
        #         nbmp = nbmp+1

        # # find the proton energ(ies) of missing bmp
        # mEn = []
        # # mbmp = []
        # bmps = [] # bmp locations
        # dEn = [] # energies of duplicated bmp loc
        # for i in range(1, nb+1):
        #     me = f'-PRO_EN_{str(i)}-'
        #     mb = f'-BMP_LOC_{str(i)}-'
        #     if values[mb] in bmps: # find the duplicated bmp energy
        #         me_1 = f'-PRO_EN_{str(i-1)}-'
        #         dEn.append(values[me_1])
        #         dEn.append(values[me])
        #     else:
        #         bmps.append(values[mb])
        #     if values[mb] =='':
        #         mEn.append(values[me])



        # find energ(ies) of missing bmps
        try:
            if mEn:
                msg = ['Missing bmp location(s) for ']
                for e in mEn:
                    msg.append(f'{e} MeV ')
                sg.popup('ERROR MESSAGE!', f'{msg}')
                continue

        except: # '' is not found
            pass

        # find energ(ies) of missing bmps
        try:
            if dEn:
                dEn = list(set(dEn))
                sg.popup('ERROR MESSAGE!', f'duplicated bmp location(s) found at {dEn} MeV')
                continue

        except: # no duplicated bmp locations
            pass

        # ## error catch energy error
        try:
            for e in aEn:
                float(e)

        except ValueError:
            sg.popup('ERROR MESSAGE!', f' Energy {e} MeV is not a float.')
            continue

        # ## error catch non-bmp
        non_bmp = []
        for f in abmp:
            if ".bmp" not in f:
                non_bmp.append(f)
        try:
            if non_bmp:
                sg.popup('ERROR MESSAGE!', f' This is not a bmp file:  {non_bmp}')
                continue
        except:
            pass


        # ## change directory and save data
        window.close()

        # ## start analysis when gantry, gantry angle and operator(s) are correctly filled.
        spotpatterns = {}
        # for i in range(1, nbmp+1):
        for i in rbmp:
            str1 = f'-PRO_EN_{str(i)}-'
            str2 = f'-BMP_LOC_{str(i)}-'
            # print(f'-------------------------')
            # print(f'>>>energy: {values[str1]}')
            # print(f'-------------------------')
            spotpatterns.update({values[str1]: spm.SpotPattern(values[str2])})

        all_data, device= spot_data(values, spotpatterns)

        # ## get measurement date
        adate = db.get_mea_time(spotpatterns)
        date = adate.strftime('%Y-%m-%d')

        result_folder = f'results_{date}'

        path_to_bmp, bmp = os.path.split(values['-BMP_LOC_1-'])
        result_dir = os.path.dirname(path_to_bmp)

        os.chdir(result_dir)

        fpath = os.path.join(result_dir, result_folder)

        if os.path.isdir(result_folder):
            print(f'The content in your current result folder is going to be overwritten!')
            os.chdir(result_folder)
        else:
            os.chdir(result_dir)
            os.mkdir(result_folder)
            os.chdir(result_folder)

        # ## start analysis
        df = []
        for key in all_data.keys():
            df.extend(all_data[key][:])

        df = pd.DataFrame(df, columns = db_cols)
        df = spf.calc_shifts(df, device)

        # ## output data to excel file
        df.to_excel('result.xlsx')

        # ## absolute plot
        fg.plot_spot_grid(df, device, tolerance = 2)
        fg.plot_shifts(df, device, tolerance = 2)
        fg.plot_shifts_by_energy(df, device, tolerance =2 )
        fg.plot_shifts_by_pos(df, device, tolerance = 2 )

        # # relative plot
        fg.plot_spot_grid(df, device, tolerance=1)
        fg.plot_shifts(df, device, tolerance=1)
        fg.plot_shifts_by_energy(df, device, tolerance =1 )
        fg.plot_shifts_by_pos(df, device, tolerance = 1 )

        fg.plot_distribution(df)
        fg.plot_fwhm(df)


        rp.make_table(df, aEn)
        comments = values['-COMMENT-']
        rp.spot_report(df, p1, p2, fpath, gr_path, prof_path, comments, aEn)

        # ## Data to proton database
        window2 = make_window_after_reviewing_data(theme)
        event2, values2 = window2.read()

        window2.close()


        rp.make_table(df, aEn)
        comments = values['-COMMENT-'] + ' ' + values2['-COMMENT2-']
        rp.spot_report(df, p1, p2, fpath, gr_path, prof_path, comments, aEn)

        if event2 == 'Submit':
            # push data to the Database
            print(f'Pushing data to the database ...')

            push_session = session_result(values, values2, spotpatterns)
            if push_session == True:
                for key in all_data.keys():
                    db.push_spot_data(DATABASE_DIR, all_data[key])
        elif event2 == 'Cancel' or sg.WIN_CLOSED:
            print(f'>> The code has completed data analysis, printed figures, output a report and an excel file. \n However, NOTHING has gone to the proton database!')
            break


        return



if __name__ == '__main__':

    main()
