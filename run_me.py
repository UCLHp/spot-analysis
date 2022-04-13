import pandas as pd
import os
import numpy as np
import easygui as eg


import matplotlib.pyplot as plt
import PySimpleGUI as sg

import figures as fg
import spot_position_mod as spm
import spot_position_func as spf
import database as db
import constants as cs
import report as rp


operators = cs.operators
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
    # warning = [sg.Text('Operator 2 is required when Operator 1 cannot sign off the spot grid QA.')]
    person_1 = [sg.Text('Operator 1: '), sg.Combo(values= operators, key = '-person1-')]
    person_2 = [sg.Text('Operator 2: '), sg.Combo(values= operators, key = '-person2-')]
    # warning = [sg.Frame('Reminder: ', [[sg.Text('Operator 2 is required when Operator 1 cannot sign off the spot grid QA.')], person_1 + person_2])]
    gantry = [sg.Text('Gantry: '), sg.Combo(values = gantries, key = '-gantry-')]
    gantry_angle = [sg.Text('Gantry angle: '), sg.InputText(size = (5, 1), key = '-gantry_angle-')]
    col_titles = [sg.Text('Proton energy (MeV)', size = (15, 1), justification = 'l'), sg.Text('Bmp picture locations', size = (20, 1), justification = 'l')]
    ent1 = [sg.Text('(1)'), sg.InputText(size = (10, 1), key = '-pro_en_1-', default_text = '70'), sg.Text('@'), sg.InputText(key = '-bmp_loc_1-'), sg.FileBrowse()]
    ent2 = [sg.Text('(2)'), sg.InputText(size = (10, 1), key = '-pro_en_2-', default_text = '100'), sg.Text('@'), sg.InputText(key = '-bmp_loc_2-'), sg.FileBrowse()]
    ent3 = [sg.Text('(3)'), sg.InputText(size = (10, 1), key = '-pro_en_3-', default_text = '150'), sg.Text('@'), sg.InputText(key = '-bmp_loc_3-'), sg.FileBrowse()]
    ent4 = [sg.Text('(4)'), sg.InputText(size = (10, 1), key = '-pro_en_4-', default_text = '200'), sg.Text('@'), sg.InputText(key = '-bmp_loc_4-'), sg.FileBrowse()]
    ent5 = [sg.Text('(5)'), sg.InputText(size = (10, 1), key = '-pro_en_5-', default_text = '240'), sg.Text('@'), sg.InputText(key = '-bmp_loc_5-'), sg.FileBrowse()]
    comment = [sg.Text('Comments: '), sg.InputText(size = (50, 1), key = '-comment-')]
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
    comment2 = [sg.Text('Comments: '), sg.InputText(size = (50, 1), key = '-comment2-')]

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
    machine_name = 'Gantry ' + gui_values['-gantry-']
    # session = 1234
    device = 'XRV-' +spotpatterns['240'].output.device
    operator1 = gui_values['-person1-']
    operator2 = gui_values['-person2-']
    comment = gui_values['-comment-'] + ' ' + values2['-comment2-']

    result = [adate, machine_name, device, operator1, operator2, comment, None]

    # push the session result to the session table in the ASSESS Database
    push_result = db.push_session_data(DATABASE_DIR, result)

    # print(f'adate: {adate}  || machine_name: {machine_name} || session: {session} || device : {device} || operator1:{operator1}')
    return push_result

def spot_data(gui_values, spotpatterns):
    ''' gui_values: a dict containing the output of the PySimpleGUI
        spotpatterns: a dict containing the SpotPattern object corresponding to the proton energy'''

    # get the latest measurement date and time from five measurements
    adate = db.get_mea_time(spotpatterns)

    machine_name = 'Gantry ' + gui_values['-gantry-']
    gantry_angle = gui_values['-gantry_angle-']

    en =  sorted([int(key) for key in spotpatterns.keys()], reverse = True)
    all_data = {}

    # debug abnormal gradient ratio
    abn_gr = []

    for e in en:
        mea_spot_loc = spotpatterns[str(e)].output.spots_info
        device = 'XRV-' + spotpatterns[str(e)].output.device
        mloc = spotpatterns[str(e)].output.mloc
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
    window = make_window(theme) #comment off to test

    while True:
        event, values = window.read() #comment off to test

# -----------------------------------------------------------------------------------
# # ------------------------------------ debug---------------------------------------
# -----------------------------------------------------------------------------------
        # event = 'Submit'

        # values = {'-person1-': 'KC', '-person2-': 'TNC', '-gantry-': '3', '-gantry_angle-': '0', '-pro_en_1-': '70', '-bmp_loc_1-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0001_70/00000001.bmp', 'Browse': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0001_70/00000001.bmp', '-pro_en_2-': '100', '-bmp_loc_2-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0002_100/00000001.bmp', 'Browse0': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0002_100/00000001.bmp', '-pro_en_3-': '150', '-bmp_loc_3-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0003_150/00000001.bmp', 'Browse1': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0003_150/00000001.bmp', '-pro_en_4-': '200', '-bmp_loc_4-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0004_200/00000001.bmp', 'Browse2': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0004_200/00000001.bmp', '-pro_en_5-': '240', '-bmp_loc_5-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0005_240/00000001.bmp', 'Browse3': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/my_spot_analysis/dummyData/G3_XRV4000_2022_03_03/run01_zero1/2022_0303_0005_240/00000001.bmp', '-comment-': ''}

         # ## C:\Users\KAWCHUNG\OneDrive - NHS\python_code\dummyData\2022_01_04_xrv3000_G1_VR
        # values = {'-person1-': 'VR', '-person2-': '', '-gantry-': '1', '-gantry_angle-': '0', '-pro_en_1-': '70', '-bmp_loc_1-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_240_2022_0104_0011/00000001.bmp', 'Browse': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_240_2022_0104_0011/00000001.bmp', '-pro_en_2-': '100', '-bmp_loc_2-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_200_2022_0104_0012/00000001.bmp', 'Browse0': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_200_2022_0104_0012/00000001.bmp', '-pro_en_3-': '150', '-bmp_loc_3-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_150_2022_0104_0013/00000001.bmp', 'Browse1': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_150_2022_0104_0013/00000001.bmp', '-pro_en_4-': '200', '-bmp_loc_4-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_100_2022_0104_0014/00000001.bmp', 'Browse2': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_100_2022_0104_0014/00000001.bmp', '-pro_en_5-': '240', '-bmp_loc_5-': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_70_2022_0104_0015/00000001.bmp', 'Browse3': 'C:/Users/KAWCHUNG/OneDrive - NHS/python_code/dummyData/2022_01_04_xrv3000_G1_VR/0_70_2022_0104_0015/00000001.bmp', '-comment-': ''}

        print(f'values: {values}')

# -----------------------------------------------------------------------------------
# # ------------------------------------ debug---------------------------------------
# -----------------------------------------------------------------------------------
        # ## get the operators
        p1 = values['-person1-']
        p2 = values['-person2-']

        # ## change directory and save data
        path = values['-bmp_loc_1-'].split(os.sep)
        result_folder = 'result'

        path_to_bmp, bmp = os.path.split(values['-bmp_loc_1-'])
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

        # ## reject duplicated operators
        if values['-person1-'] == values['-person2-']:
            print(f' >>> same operator 1 and operator 2! That is NOT okay.')
            break

        # ## start analysis when gantry, gantry angle and operator(s) are correctly filled.
        spotpatterns = {}
        if event == 'Submit' and values['-gantry-'] != '' and values['-gantry_angle-'] != '' and values['-person1-'] != '' :
            en = []
            bmp_dir = []
            for i in range(1,6):
                str1 = '-pro_en_%s-' % str(i)
                str2 = '-bmp_loc_%s-' % str(i)
                if values[str1] not in en:
                    en.append(values[str1])
                else:
                    sg.popup('You have entred %s MeV twice! Please have a look at the Proton energy column!' % str(values[str1]))
                    break

                if values[str2] not in bmp_dir:
                    bmp_dir.append(values[str2])
                else:
                    sg.popup('Double check your bmp location column! Duplicated entry detected' )
                    break # break the loop when the same bmp location is entred, at least, twice.
                    sg.WIN_CLOSED

                # ## create spotpattern objects in a Dictionary
                spotpatterns.update({values[str1]: spm.SpotPattern(values[str2])})
        else:
            sg.popup('ERROR MESSAGE!','You hit SUBMIT but either your Gantry, Gantry angle and Operator 1 is empty. Please have a look and try again!' )
            break


        all_data, device= spot_data(values, spotpatterns)



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


        rp.make_table(df)
        rp.spot_report(df, p1, p2, fpath, gr_path, prof_path)

        window.close()

        # ## Data to proton database
        window2 = make_window_after_reviewing_data(theme)
        event2, values2 = window2.read()

        window2.close()

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
    theme = 'DefaultNoMoreNagging'
    main()
