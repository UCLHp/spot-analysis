import traceback

import matplotlib
matplotlib.use('TkAgg')

import os
import sys
import io
import warnings
from os.path import join, isfile
import xlsxwriter
import logos_module as lm
import log_generator as lg
import spot_comparison as sc
import database as db
import matplotlib.pyplot as plt
import numpy as np

'''
This Script creates a report containing single and double 2D Gaussian fits to
spot images acquired using the LOGOS 3000 or 4000 scintillation detector.
'''


def write_chart(workbook, worksheet, x, key, title, datacol1, datacol2,
                datacol3, datacol4, pastecell):
    '''
    4 graphs are produced per excel worksheet, this function avoids duplication
    x is for the x axis
    pastecell is where the graph will be pasted
    key is the
    '''
    key=str(key)
    chart1 = workbook.add_chart({'type': 'scatter'})
    chart1.add_series({
        'name':       'Raw data',
        'categories': "".join("=" + key + f"!${datacol1}$9:${datacol1}$"
                                        + str(8+len(x))),
        'values':     "".join("=" + key + f"!${datacol2}$9:${datacol2}$"
                                        + str(8+len(x))),
        'line': {'color': 'red', 'width': 1, },
        'marker': {'type': 'none'},
    })
    chart1.add_series({
        'name':       'Single Fit Model',
        'categories': "".join("="+key+f"!${datacol1}$9:${datacol1}$"+str(8+len(x))),
        'values':     "".join("="+key+f"!${datacol3}$9:${datacol3}$"+str(8+len(x))),
        'line': {'color': 'blue', 'width': 1, },
        'marker': {'type': 'none'},
    })
    chart1.add_series({
        'name':       'Double Fit Model',
        'categories': "".join("="+key+f"!${datacol1}$9:${datacol1}$"+str(8+len(x))),
        'values':     "".join("="+key+f"!${datacol4}$9:${datacol4}$"+str(8+len(x))),
        'line': {'color': 'green', 'width': 1, },
        'marker': {'type': 'none'},
    })
    chart1.set_title({'name': f'{title}'})
    chart1.set_x_axis({'name': 'Central Axis (mm)'})
    chart1.set_y_axis({'name': 'Relative intensity'})
    chart1.set_style(11)
    worksheet.insert_chart(pastecell, chart1)


def produce_spot_dict(log_dir, acquiredfoldersdir):
    '''
    Function to produce spot profiles for entry into our TPS
    For a directory of acquired single spot tif files using the LOGOS 3/4000
    Single and double 2D Gaussians are fitted using the astropy library
    we then return the required profiles in excel for review
    '''

    spot_dataset = lm.create_spot_dataset(log_dir, acquiredfoldersdir) # create a dataframe from the log to lookup files
    print(f"Dataframe created from the log ({len(spot_dataset)} rows).")  # code status message

    # creating a dict for loop
    print("Creating data dictionary......")  # code status message
    spots = {} # key:(GA, RS, distance, energy)
    for index, row in spot_dataset.iterrows():
        # dataframe info
        folder = row['Folder']
        energy = row['Energy']
        ga = row['GA']
        rs = row['RS']
        dist = row['Distance']

        # Image file may be acquired as either bmp or tif
        extension = ""
        img_dir = join(acquiredfoldersdir, folder)
        if isfile( join(img_dir, row['Image']+'.tif') ):
            extension = '.tif'
        elif isfile( join(img_dir, row['Image']+'.bmp') ):
            extension = '.bmp'
        else:
            print("ERROR: No tif or bmp file found for {}".format(join(img_dir, row['Image'])) )
            raise SystemExit
        image_name = row['Image'] + extension
        spotimage = join(img_dir, image_name)

        # filling the dict
        spots[ga, rs, dist, energy] = lm.Spot(spotimage, ga, rs, dist, energy)

    return spots

# workbook = xlsxwriter.Workbook(join(save_dir, 'TPS_Profiles.xlsx'), {'nan_inf_to_errors': True})

def log10_with_zero(list):
    '''Function that leaves zero as zero and computes log10 otherwise'''
    log10_list = []
    for i in list:
        if i == 0:
            log10_list.append(0)
        else:
            log10_list.append(np.log10(i))

    return log10_list

def plot_fits(spots, ga, rs, dist):
    '''Create plots to review spot profiles'''

    save_dir = save_path # save the fitting excel results to the Results folder
    # Create empty Excel file to write results to, with ability to write errors as 0
    savename = f'Fits_GA{ga}_RS{rs}_Dist{dist}.xlsx'
    workbook = xlsxwriter.Workbook(join(save_dir, savename), {'nan_inf_to_errors': True})
    # Summary worksheet to contain parameters for all energies
    summary = workbook.add_worksheet('Summary')
    summary.write('B3', 'Energy')
    summary.merge_range('C2:I2', 'Single Gaussian Fit')
    summary.merge_range('J2:R2', 'Double Gaussian Fit')
    summary.write_row('C3', list(lm.models.Gaussian2D().param_names) + list(lm.doubl_gaus().param_names))
    # counter used to add line per image analysed
    counter = 0

    temp_dir = join(save_dir, 'ImagesForDeletion')
    os.mkdir(temp_dir)

    for key in sorted(spots):
        # Write key and parameter values to summary sheet
        summary.write(f'B{counter+4}', key)
        summary.write_row(f'C{counter+4}', list(spots[key].singlefit.parameters) + list(spots[key].doublefit.parameters))

        # Create and write sheet for specific image
        worksheet = workbook.add_worksheet(str(key))

        worksheet.merge_range('B2:B3', 'Single Params')
        worksheet.merge_range('B4:B5', 'Double Params')

        # Replicates data on summary sheet
        worksheet.write_row('C2', list(spots[key].singlefit.param_names))
        worksheet.write_row('C3', list(spots[key].singlefit.parameters))
        worksheet.write_row('C4', list(spots[key].doublefit.param_names))
        worksheet.write_row('C5', list(spots[key].doublefit.parameters))

        # Main data table titles
        worksheet.merge_range('B7:E7', 'Horizontal Profile')
        worksheet.merge_range('F7:I7', 'Vertical Profile')
        worksheet.merge_range('J7:O7', 'Values for Log Plots')
        worksheet.write_row('B8', ['Distance', 'Image intensity', 'Single Fit Intensity', 'Double Fit Intensity'])
        worksheet.write_row('F8', ['Distance', 'Image intensity', 'Single Fit Intensity', 'Double Fit Intensity'])
        worksheet.write_row('J8', ['LOG Horizontal Image intensity', 'LOG Horizontal Single Fit Intensity', 'LOG Horizontal Double Fit Intensity'])
        worksheet.write_row('M8', ['LOG Vertical Image intensity', 'LOG Vertical Single Fit Intensity', 'LOG Vertical Double Fit Intensity'])

        # The lines for plot are taken from the "centre" defined by the module
        worksheet.write_column('B9', spots[key].adjustedcropprofiles[0])
        worksheet.write_column('C9', spots[key].adjustedcropprofiles[1])
        worksheet.write_column('D9', spots[key].singlefitarray[spots[key].cropspotcentre[1]])
        worksheet.write_column('E9', spots[key].doublefitarray[spots[key].cropspotcentre[1]])

        # list comp to take 'i'th item in each row in 2D array
        worksheet.write_column('F9', spots[key].adjustedcropprofiles[2])
        worksheet.write_column('G9', spots[key].adjustedcropprofiles[3])
        worksheet.write_column('H9', [item[spots[key].cropspotcentre[0]] for item in spots[key].singlefitarray])
        worksheet.write_column('I9', [item[spots[key].cropspotcentre[0]] for item in spots[key].doublefitarray])

        # Writing log values for log plots
        worksheet.write_column('J9', log10_with_zero(spots[key].adjustedcropprofiles[1])) # contains zeros
        worksheet.write_column('K9', np.log10(spots[key].singlefitarray[spots[key].cropspotcentre[1]]))
        worksheet.write_column('L9', np.log10(spots[key].doublefitarray[spots[key].cropspotcentre[1]]))
        worksheet.write_column('M9', log10_with_zero(spots[key].adjustedcropprofiles[3])) # contains zeros
        worksheet.write_column('N9', [np.log10(item[spots[key].cropspotcentre[0]]) for item in spots[key].singlefitarray])
        worksheet.write_column('O9', [np.log10(item[spots[key].cropspotcentre[0]]) for item in spots[key].doublefitarray])

        # Create plots using function defined earlier
        write_chart(workbook, worksheet, spots[key].adjustedcropprofiles[0], key, 'Horizontal Profile', 'B', 'C', 'D', 'E', 'K5')
        write_chart(workbook, worksheet, spots[key].adjustedcropprofiles[0], key, 'Horizontal Profile log 10', 'B', 'J', 'K', 'L', 'S5')
        write_chart(workbook, worksheet, spots[key].adjustedcropprofiles[2], key, 'Vertical Profile', 'F', 'G', 'H', 'I', 'K20')
        write_chart(workbook, worksheet, spots[key].adjustedcropprofiles[2], key, 'Vertical Profile log 10', 'F', 'M', 'N', 'O', 'S20')

        # Save difference images in temporary directory

        plt.imsave(temp_dir + f'\\{key}_diff_image1.png', spots[key].singlefitarray - spots[key].normcropspot)
        plt.imsave(temp_dir + f'\\{key}_diff_image2.png', spots[key].doublefitarray - spots[key].normcropspot)

        # Insert saved images into the excel file
        # Scal will need to be adjusted with image size from LOGOS
        worksheet.insert_image('K35', temp_dir + f'\\{key}_diff_image1.png', {'x_scale':4, 'y_scale':4})
        worksheet.insert_image('S35', temp_dir + f'\\{key}_diff_image2.png', {'x_scale':4, 'y_scale':4})

        counter+=1

    workbook.close()

    for file in os.listdir(temp_dir):
        os.remove(temp_dir+'\\'+file)
    os.rmdir(temp_dir)

class CapturePrints: # class to capture all print messages
    def __init__(self):
        self.buffer = io.StringIO() # text buffer to store all print messages
        self.stdout = sys.stdout  # keep console

    def write(self, message):
        self.stdout.write(message)  # show in console immediately
        self.buffer.write(message)  # save to buffer

    def flush(self): # ensure console and buffer flush properly
        self.stdout.flush()
        self.buffer.flush()

    def getvalue(self):
        return self.buffer.getvalue() # return everything as a single string

####################
# Running the code #
####################
# initiating code message capture
capture = CapturePrints()
initial_capture = sys.stdout

try:
    sys.stdout = capture # start capturing all printed messages

    #___Selecting the acquisition folder___#
    import platform
    print("Launching GUI......") # code status message
    print("")
    acquiredfoldersdir, gantry, Op1, Op2 = lg.file_gui() # GUI to select the Logos data folders + create Results folder
    col_no, folders, image, GA, RS, dist, eng, save_path, CamOrient = lg.info_gui(acquiredfoldersdir) # GUI to provide acquisition info for each folder

    print(f"[{gantry} selected]") # code status message
    print("")

    #___Creating the acquisition log___#
    log_dir = lg.create_log(col_no,folders,image,GA,RS,dist,eng,save_path) # creating the acquisition log
    print(f"Acquisition log created ({len(col_no)} rows).") # code status message

    #___Creating a data dict___#
    spots_dict = produce_spot_dict(log_dir, acquiredfoldersdir) # create spots dict for fitting {GA, RS, distance, energy}; Dataframe status message is within the function
    print("Data dictionary created.") # code status message

    grouped = {} # grouping the spots into sets (i.e. what GA, RS, distance)
    for key, spot in spots_dict.items():
        set_info = key[:3] # info for the set
        energy = key[3] # energy of spot

        if set_info not in grouped:# creating a new nestted dict for a new set of spots
            grouped[set_info] = {}

        grouped[set_info][energy] = spot # filling the spots with energy as the key in the nested dict
    print("Data dictionary grouped into sets.") # code status message
    print("")

    #___Fitting for each set of data___#
    print("____________Fitting spots____________") # code status message
    warnings.filterwarnings( # warning message that doesn't affect the fitting; will ignore the message to avoid confusion
        "ignore",
        message="Values in x were outside bounds during a minimize step, clipping to bounds",
        category=RuntimeWarning
    )

    for key, set in grouped.items():
        # Set labels
        ga = key[0]
        rs = key[1]
        dist = key[2]
        print(f"Fitting for GA{ga}, RS{rs}, Dist{dist}......") # code status message
        for energy, bmp in set.items():
            set[energy].create_fits()

        print("Creating Excel results......") # code status message
        plot_fits(set, ga, rs, dist)
        print("Results created.") # code status message
        print("")

    #___Plotting comparison graphs___#
    print("____________Plotting comparison graphs____________") # code status message
    sc.spot_comparison(gantry,folders,save_path)

    #___Writing to DB__#
    print("____________Pushing data to DB____________")
    print("Connecting to the Database......")
    db_write, path, comments = db.test_db_connection()

    if db_write == 'Yes':
        db.write_to_db(acquiredfoldersdir, gantry, CamOrient, Op1, Op2, comments)
    else:
        pass

    #___END___#
    input("Press Enter to save all code messages!")

except Exception:
    traceback.print_exc(file=capture) # capture printed messages till error + error messages

finally:
    # end capture
    sys.stdout = capture.stdout
    with open(save_path + "/CodeLog.txt", "w") as f: # save everything in a .txt
        f.write(capture.getvalue())