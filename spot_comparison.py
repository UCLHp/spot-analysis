import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def spot_comparison(gantry, folders, save_dir):
    '''
    Function to loop through every Excel files in the Results folder and compare them with the Excel files in the spot
    profile reference folder. For a matching set of setup, the function will plot a graph with four subplots:

    Top-Left:        x sigma of the single Gaussian fit of the spots

    Top-Right:       y sigma of the single Gaussian fit of the spots

    Bottom-Left:     Percentage differences of the FWHM of the measured spots and the gantry reference data

    Bottom-Right:    Percentage differences of the FWHM of the measured spots and the TPS data
    '''

    print(f"[{gantry} selected]") # code status message
    print("")

    # reference data path #
    TPS_dir = r"\\9.40.120.20\pbtqadata\Routine QA\Annual Checks\Reference Data\Spot Profile Ref\TPS"  # TPS data path
    reference_dir = r"\\9.40.120.20\pbtqadata\Routine QA\Annual Checks\Reference Data\Spot Profile Ref" # commissioning data path

    # Selecting commissioning data path according to the gantry selected #
    if gantry == "Gantry 1":
        reference_dir = reference_dir + "\G1"
    elif gantry == "Gantry 2":
        reference_dir = reference_dir + "\G2"
    elif gantry == "Gantry 3":
        reference_dir = reference_dir + "\G3"
    elif gantry == "Gantry 4":
        reference_dir = reference_dir + "\G4"

    # Looking for dates in the txt files #
    acquiredfoldersdir = os.path.dirname(save_dir)

    date_list = [] # empty list for dates
    for i in folders:
        outputfile = os.path.join(acquiredfoldersdir, i, "output.txt") # looping through every Logos folders

        with open(outputfile, "r") as f: # reading output.txt files for date
            lines = f.readlines()
            date_str = lines[-1][5:24]  # fetching date string from the last line
            date = datetime.strptime(date_str, "%H:%M:%S %m/%d/%Y")
            date_list.append(date)

    start = min(date_list).date().isoformat() # date of the 1st measurement; use later on for dates on graph
    end = max(date_list).date().isoformat() # date of the last measurement; use later on for dates on graph

    ####################################################################################################################

    # looking up the fitting Excel files and compare it to the files inside the gantry reference folder #
    for fits_file in os.listdir(save_dir):
        fits_path = os.path.join(save_dir, fits_file)  # file path of everything in the Results folder
        fits = fits_file[fits_file.find("A")+1:]  # acquisition info; use GA for gantry angle
        for ref_file in os.listdir(reference_dir):
            ref_path = os.path.join(reference_dir, ref_file)  # file path of gantry reference data
            ref = ref_file[ref_file.find("G")+1:]  # acquisition info; use G for gantry angle

            # comparing the acquisition info of the fits to the reference
            if fits == ref:
                # looking up the TPS reference file that matches the RS and distance
                tps_file = "Fits_G90_" + ref_file[ref_file.find("R"):]
                tps_path = os.path.join(TPS_dir, tps_file) # file path of TPS data
                print(f"Reference data used: {ref_path}") # code status message
                print(f"TPS data used: {tps_path}") # code status message

                #################
                # Reading Excel #
                #################
                # Turning fitting data to list
                data_df = pd.read_excel(fits_path, header=None)
                data_df = pd.DataFrame.dropna(data_df, thresh=3)
                data_df = pd.DataFrame.transpose(data_df)
                fit_list = data_df.values.tolist()
                # Turning commissioning data to list
                ref_df = pd.read_excel(ref_path, header=None)
                ref_df = pd.DataFrame.dropna(ref_df, thresh=3)
                ref_df = pd.DataFrame.transpose(ref_df)
                ref_list = ref_df.values.tolist()
                # Turning TPS data to list
                tps_df = pd.read_excel(tps_path, header=None)
                tps_df = pd.DataFrame.dropna(tps_df, thresh=3)
                tps_df = pd.DataFrame.transpose(tps_df)
                tps_list = tps_df.values.tolist()

                ####################
                # Lists for graphs #
                ####################
                energy = ref_list[1][1:]

                # TPS data
                tps_x = tps_list[5][1:]
                tps_y = tps_list[6][1:]

                # Reference data
                ref_x = ref_list[5][1:]
                ref_y = ref_list[6][1:]
                # Tolerance from reference
                upper_ref_x = [i * 1.1 for i in ref_x]
                lower_ref_x = [i * 0.9 for i in ref_x]
                upper_ref_y = [i * 1.1 for i in ref_y]
                lower_ref_y = [i * 0.9 for i in ref_y]

                # Fit data
                data_x = fit_list[5][1:]
                data_y = fit_list[6][1:]

                # Date of measurement
                if start == end:  # checking if start and end date on data folder is the same
                    result_date = "measured on " + start
                else:
                    result_date = "measured between " + start + " - " + end

                # FWHM
                fwhm_data = [2 * np.sqrt(2*np.log(2)) * (x + y) / 2 for x, y in zip(data_x, data_y)]
                fwhm_ref = [2 * np.sqrt(2*np.log(2)) * (x + y) / 2 for x, y in zip(ref_x, ref_y)]
                fwhm_tps = [2 * np.sqrt(2 * np.log(2)) * (x + y) / 2 for x, y in zip(tps_x, tps_y)]
                # % diff
                ref_diff = [ (data - ref) / ref * 100
                             for data, ref in zip(fwhm_data, fwhm_ref)] # % diff relative to ref
                tps_diff = [(data - tps) / tps * 100
                            for data, tps in zip(fwhm_data, fwhm_tps)]  # % diff relative to tps

                ##########
                # Graphs #
                ##########
                fig, axs = plt.subplots(2, 2, figsize=(16, 12))
                # Overview settings
                fig.suptitle(f"Spot Profile Analysis for Gantry{gantry[-1]}_GA{fits[:-5]} ({result_date})") # name graph according to info match

                # x sigma graph (perpendicular to camera)
                axs[0,0].plot(energy, data_x, 'kx', label='Measured') # top left
                axs[0,0].plot(energy, upper_ref_x, 'r--', label='Commissioning data ±10%')
                axs[0,0].plot(energy, lower_ref_x, 'r--')
                # Graph Settings
                axs[0,0].set_title("Gaussian fit for the profile perpendicular to the camera")
                axs[0,0].set_xlabel("Energy / MeV")
                axs[0,0].set_ylabel("Sigma")
                axs[0,0].set_xlim(60, 250)
                axs[0,0].legend(loc='best')
                axs[0,0].grid()

                # y sigma graph (parallel to camera)
                axs[0,1].plot(energy, data_y, 'kv', label='Measured') # top right
                axs[0,1].plot(energy, upper_ref_y, 'r--', label='Commissioning data ±10%')
                axs[0,1].plot(energy, lower_ref_y, 'r--')
                # Graph Settings
                axs[0,1].set_title("Gaussian fit for the profile parallel to the camera")
                axs[0,1].set_xlabel("Energy / MeV")
                axs[0,1].set_ylabel("Sigma")
                axs[0,1].set_xlim(60, 250)
                axs[0,1].legend(loc='best')
                axs[0,1].grid()

                ## FWHM vs ref graph ##
                axs[1,0].plot(energy, ref_diff, 'k.', label='Measured') # bottom left
                axs[1,0].axhline(-10, color='red', linestyle='--', label='Commissioning data ±10%')
                axs[1,0].axhline(10, color='red', linestyle='--')
                # Graph Settings
                axs[1,0].set_title("Percentage difference of FWHM relative to commissioning data")
                axs[1,0].set_xlabel("Energy / MeV")
                axs[1,0].set_ylabel("Commissioning diff [ (data - ref) / ref ] / %") # (data - ref) / ref * 100
                axs[1,0].set_xlim(60, 250)
                axs[1,0].set_ylim(-15, 15)
                axs[1,0].legend(loc='best')
                axs[1,0].grid()

                ## FWHM vs tps graph ##
                axs[1,1].plot(energy, tps_diff, 'k.', label='Measured') # bottom left
                axs[1,1].axhline(-10, color='red', linestyle='--', label='TPS data ±10%')
                axs[1,1].axhline(10, color='red', linestyle='--')
                # Graph Settings
                axs[1,1].set_title("Percentage difference of FWHM relative to the TPS")
                axs[1,1].set_xlabel("Energy / MeV")
                axs[1,1].set_ylabel("TPS diff [ (data - tps) / tps ] / %") # (data - tps) / tps * 100
                axs[1,1].set_xlim(60, 250)
                axs[1,1].set_ylim(-15, 15)
                axs[1,1].legend(loc='best')
                axs[1,1].grid()


                # Saving graph in result folder
                save = os.path.join(save_dir, f"Graph_{fits_file[5:-5]}.png")
                plt.savefig(save)
                print(f"Graph generated for: {fits_file} ") # code status message
                print("")
                #plt.show()