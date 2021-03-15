import os
import xlsxwriter
import easygui as eg
import logos_module as lm
import matplotlib.pyplot as plt
import numpy as np
from astropy.modeling import models, fitting

'''
This Script creates a report containing single and double 2D Gaussian fits to
spot images acquired using the LOGOS 3000 or 4000 scintillation detector.
'''

# This decorator allows you to create a "model" class as defined by astropy


def write_chart(workbook, worksheet, x, key, title, datacol1, datacol2,
                datacol3, datacol4, pastecell):
    '''
    4 graphs are produced per excel worksheet, this function avoids duplication
    '''

    chart1 = workbook.add_chart({'type': 'scatter'})
    chart1.add_series({
        'name':       'Raw data',
        'categories': "".join("=" + key + f"!${datacol1}$9:${datacol1}$"
                                        + str(8+len(x[0]))),
        'values':     "".join("=" + key + f"!${datacol2}$9:${datacol2}$"
                                        + str(8+len(x[0]))),
        'line': {'color':'red', 'width': 1,},
        'marker': {'type':'none'},
    })
    chart1.add_series({
        'name':       'Single Fit Model',
        'categories': "".join("="+key+f"!${datacol1}$9:${datacol1}$"+str(8+len(x[0]))),
        'values':     "".join("="+key+f"!${datacol3}$9:${datacol3}$"+str(8+len(x[0]))),
        'line': {'color':'blue', 'width': 1,},
        'marker': {'type':'none'},
    })
    chart1.add_series({
        'name':       'Double Fit Model',
        'categories': "".join("="+key+f"!${datacol1}$9:${datacol1}$"+str(8+len(x[0]))),
        'values':     "".join("="+key+f"!${datacol4}$9:${datacol4}$"+str(8+len(x[0]))),
        'line': {'color':'green', 'width': 1,},
        'marker': {'type':'none'},
    })
    chart1.set_title ({'name': f'{title}'})
    chart1.set_x_axis({'name': 'Central Axis (mm)'})
    chart1.set_y_axis({'name': 'Relative intensity'})
    chart1.set_style(11)
    worksheet.insert_chart(pastecell, chart1)


def produce_tps_profile_data():
    '''
    Function to produce spot profiles for entry into our TPS
    For a directory of acquired single spot tif files using the LOGOS 3/4000
    Single and double 2D Gaussians are fitted using the astropy library
    we then return the required profiles in excel for review
    '''

    log_dir = "C:\\Users\\csmgi\\Desktop\\Work\\LocalLOGOSkey01.xlsx"
    # log_dir = eg.fileopenbox('Select image acquisition log')

    if not log_dir:
        print('No log selected, code will terminate')
        input('Press enter to close window')
        raise SystemExit

    acquiredfoldersdir = "C:\\Users\\csmgi\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\QAandCommissioning\\Gantry 1\\Commissioning\\Data\\Profiles\\Raw Data\\2021_03_10-post-retune-check"
    # acquiredfoldersdir = eg.diropenbox('Select directory containing all acquired LOGOS folders')


    if not acquiredfoldersdir:
        print('No folder directory selected, code will terminate')
        input('Press enter to close window')
        raise SystemExit

    spot_dataset = lm.create_spot_dataset(log_dir, acquiredfoldersdir)

    ga_list = spot_dataset.GA.unique()
    rs_list = spot_dataset.RS.unique()
    dist_list = spot_dataset.Distance.unique()

    ga = eg.choicebox("Select Gantry Angle for fit analysis", "GA", ga_list)
    rs = eg.choicebox("Select Range Shifter", "RS", rs_list)
    dist = eg.choicebox("Select Distance", "Distance from Iso", dist_list)

    print()
    ga_subdf = spot_dataset.loc[spot_dataset['GA'] == ga]
    print(ga_subdf)


produce_tps_profile_data()
"""




    spot_dir = eg.diropenbox('Select directory containing spot images'  # ,
                             #default = DEFAULTDIR
                             )

    file_list = os.listdir(spot_dir)

    # The LOGOS detectors have a resolution in x and y that is defined at
    # calibration - these values are stored in the activescript file
    if 'activescript.txt' not in file_list:
        print('activescript.txt not found')
        print('This is required for the image resolution')
        print('Code Terminated')
        input('Press enter to close window')
        raise SystemExit
    else:
        print('activescript.txt file found\n')

    # Resolution taken from active script file
    active_script = lm.ActiveScript(os.path.join(spot_dir,'activescript.txt'))
    resolution = [active_script.CameraHRatio, active_script.CameraVRatio]

    # Only include the image files in the list, not the txt or script files
    img_types = ('.tif', '.tiff', 'jpg', '.bmp')
    image_list = [f for f in os.listdir(spot_dir) if f.endswith(img_types)]
    # Sort images into order of ascending energy

    ################ Optional image sorting for numbered images
    # image_list = sorted(image_list, key=lambda f: int(os.path.splitext(f)[0]))
    ################


    # Sequential Least Squares Programming fitting function from astropy
    # https://docs.astropy.org/en/stable/api/astropy.modeling.fitting.SLSQPLSQFitter.html#astropy.modeling.fitting.SLSQPLSQFitter
    fit_p = fitting.SLSQPLSQFitter()

    # save_dir = eg.diropenbox(title='Please Select Save Location')
    # if not save_dir:
    #     raise SystemExit
    save_dir = spot_dir
    # Unable to paste plt.imshow images directly into an excel file. Temporary
    # dir created to save images, these are imported then temp_dir is deleted
    temp_dir = os.path.join(save_dir, 'ImagesForDeletion')
    os.mkdir(temp_dir)

    # astropy used to created combined models. PSF is a single 2D gaussian
    PSF_model = models.Gaussian2D() + addition()
    #G2D is a double two D gaussian both with the addition of the background
    G2D_model = lm.twoD_Gaussian()

    # Create empty excel file to write results to, with ability to write errors as 0
    workbook = xlsxwriter.Workbook(os.path.join(save_dir, 'TPS_Profiles.xlsx'), {'nan_inf_to_errors': True})
    # Summary worksheet to contain parameters for all energies
    summary = workbook.add_worksheet('Summary')
    summary.write('B3', 'Image')
    summary.merge_range('C2:I2', 'Single Gaussian Fit')
    summary.merge_range('J2:V2', 'Double Gaussian Fit')
    summary.write_row('C3', list(PSF_model.param_names) + [] + list(G2D_model.param_names))
    # counter used to add line per image analysed
    counter = 0

    for key in image_list:
        print(f"Fitting profiles for {key.split('.')[0]}")
        spot_array = lm.image_to_array(os.path.join(spot_dir,key), norm=True)
        # spot_array = lm.csv_to_array(os.path.join(spot_dir,key))#, norm=True)

        spot_array = lm.crop_center(spot_array, 300, 300)
        # find_centre used to give fit a decent starting point
        centre = lm.find_centre(spot_array, norm=True)

        # PSF is a single 2D gaussian with offset using a compund model
        # G2D is a double 2D gaussian with offset using a compund model
        # https://docs.astropy.org/en/stable/modeling/compound-models.html
        G2D_model = lm.twoD_Gaussian(x_mean = centre[0]/resolution[0], y_mean = centre[1]/resolution[1])
        PSF_model = models.Gaussian2D(x_mean = centre[0]/resolution[0], y_mean = centre[1]/resolution[1]) + addition()
        # G2D_model = models.Gaussian2D(x_mean = centre[0]/resolution[0], y_mean = centre[1]/resolution[1]) + models.Gaussian2D(x_mean = centre[0]/resolution[0], y_mean = centre[1]/resolution[1]) + addition()

        # Meshgrid produces a coordinate pair for each pixel value
        x, y = np.meshgrid(np.arange(0,len(spot_array[0])), np.arange(0,len(spot_array)))
        # x, y = np.mgrid[:len(spot_array[0]), :len(spot_array)]

        # Dividing by resolution gives absolute distance rather than pixels
        x = np.true_divide(x, resolution[0])
        y = np.true_divide(y, resolution[1])

        # Apply fit to both models, verblevel prevents print statements
        p1 = fit_p(PSF_model, x, y, spot_array, verblevel=0)
        print('Single fit complete')
        p2 = fit_p(G2D_model, x, y, spot_array, verblevel=0)
        print('Double Fit complete, writing excel worksheet')

        # Write key and parameter values to summary sheet
        summary.write(f'B{counter+4}', key.split('.')[0])
        summary.write_row(f'C{counter+4}', list(p1.parameters) + list(p2.parameters))

        # Create and write sheet for specific image
        worksheet = workbook.add_worksheet(key)

        worksheet.merge_range('B2:B3', 'Single Params')
        worksheet.merge_range('B4:B5', 'Double Params')

        # Replicates data on summary sheet
        worksheet.write_row('C2', list(p1.param_names))
        worksheet.write_row('C3', list(p1.parameters))
        worksheet.write_row('C4', list(p2.param_names))
        worksheet.write_row('C5', list(p2.parameters))

        # Main data table titles
        worksheet.merge_range('B7:E7', 'Horizontal Profile')
        worksheet.merge_range('F7:I7', 'Vertical Profile')
        worksheet.merge_range('J7:O7', 'Values for Log Plots')
        worksheet.write_row('B8', ['Distance', 'Image intensity', 'Single Fit Intensity', 'Double Fit Intensity'])
        worksheet.write_row('F8', ['Distance', 'Image intensity', 'Single Fit Intensity', 'Double Fit Intensity'])
        worksheet.write_row('J8', ['LOG Horizontal Image intensity', 'LOG Horizontal Single Fit Intensity', 'LOG Horizontal Double Fit Intensity'])
        worksheet.write_row('M8', ['LOG Vertical Image intensity', 'LOG Vertical Single Fit Intensity', 'LOG Vertical Double Fit Intensity'])

        # x[0] represents the crossprofile distance
        # The lines for plot are taken from the "centre" defined by the module
        worksheet.write_column('B9', x[0])
        worksheet.write_column('C9', spot_array[centre[1]])
        worksheet.write_column('D9', p1(x, y)[centre[1]])
        worksheet.write_column('E9', p2(x, y)[centre[1]])

        # list comp to take 'i'th item in each row in 2D array
        worksheet.write_column('F9', [item[0] for item in y])
        worksheet.write_column('G9', [item[centre[0]] for item in spot_array])
        worksheet.write_column('H9', [item[centre[0]] for item in p1(x, y)])
        worksheet.write_column('I9', [item[centre[0]] for item in p2(x, y)])

        # Writing log values for log plots
        worksheet.write_column('J9', np.log10(spot_array[centre[1]]))
        worksheet.write_column('K9', np.log10(p1(x, y)[centre[1]]))
        worksheet.write_column('L9', np.log10(p2(x, y)[centre[1]]))
        worksheet.write_column('M9', [np.log10(item[centre[0]]) for item in spot_array])
        worksheet.write_column('N9', [np.log10(item[centre[0]]) for item in p1(x, y)])
        worksheet.write_column('O9', [np.log10(item[centre[0]]) for item in p2(x, y)])

        # Create plots using function defined earlier
        write_chart(workbook, worksheet, x, key, 'Horizontal Profile', 'B', 'C', 'D', 'E', 'K5')
        write_chart(workbook, worksheet, x, key, 'Horizontal Profile log 10', 'B', 'J', 'K', 'L', 'S5')
        write_chart(workbook, worksheet, x, key, 'Vertical Profile', 'F', 'G', 'H', 'I', 'K20')
        write_chart(workbook, worksheet, x, key, 'Vertical Profile log 10', 'F', 'M', 'N', 'O', 'S20')

        # Save difference images in temporary directory
        plt.imsave(temp_dir + f'\\{key}_diff_image1.png', p1(x,y) - spot_array)
        plt.imsave(temp_dir + f'\\{key}_diff_image2.png', p2(x,y) - spot_array)

        # Insert saved images into the excel file
        # Scal will need to be adjusted with image size from LOGOS
        worksheet.insert_image('K35', temp_dir + f'\\{key}_diff_image1.png', {'x_scale':4, 'y_scale':4})
        worksheet.insert_image('S35', temp_dir + f'\\{key}_diff_image2.png', {'x_scale':4, 'y_scale':4})

        counter+=1

    workbook.close()

    # Remove temporary images and directory
    for file in os.listdir(temp_dir):
        os.remove(temp_dir+'\\'+file)
    os.rmdir(temp_dir)

if __name__ == '__main__':
    produce_tps_profile_data()
"""
