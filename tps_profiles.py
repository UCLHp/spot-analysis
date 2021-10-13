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

    spot_dataset = lm.create_spot_dataset(log_dir, acquiredfoldersdir)

    ga_list = spot_dataset.GA.unique()
    if len(ga_list) == 1:
        ga = ga_list[0]
    else:
        ga = eg.choicebox("Select Gantry Angle for fit analysis", "GA", ga_list)
    ga_subdf = spot_dataset.loc[spot_dataset['GA'] == int(ga)]

    rs_list = ga_subdf.RS.unique()
    if len(rs_list) == 1:
        rs = rs_list[0]
    else:
        rs = eg.choicebox("Select Range Shifter", "RS", rs_list)
    rs_subdf = ga_subdf.loc[ga_subdf['RS'] == int(rs)]

    dist_list = rs_subdf.Distance.unique()
    if len(dist_list) == 1:
        dist = dist_list[0]
    else:
        dist = eg.choicebox("Select Distance", "Distance from Iso", dist_list)
    subdf = rs_subdf.loc[rs_subdf['Distance'] == int(float(dist))]

    spots = {}
    for index, row in subdf.iterrows():
        folder = row['Folder']
        image_name = row['Image'] + '.tif'
        energy = row['Energy']

        spotimage = os.path.join(acquiredfoldersdir, folder)
        spotimage = os.path.join(spotimage, image_name)
        spots[energy] = lm.Spot(spotimage, ga, rs, dist, energy)

    return spots, ga, rs, dist


# workbook = xlsxwriter.Workbook(os.path.join(save_dir, 'TPS_Profiles.xlsx'), {'nan_inf_to_errors': True})

def plot_fits(spots, ga, rs, dist):
    '''Create plots to review spot profiles'''

    save_dir = eg.diropenbox(title='Please Select Save Location')
    # Create empty excel file to write results to, with ability to write errors as 0
    savename = f'Fits_G{ga}_RS{rs}_Dist{dist}.xlsx'
    workbook = xlsxwriter.Workbook(os.path.join(save_dir, savename), {'nan_inf_to_errors': True})
    # Summary worksheet to contain parameters for all energies
    summary = workbook.add_worksheet('Summary')
    summary.write('B3', 'Energy')
    summary.merge_range('C2:I2', 'Single Gaussian Fit')
    summary.merge_range('J2:R2', 'Double Gaussian Fit')
    summary.write_row('C3', list(lm.models.Gaussian2D().param_names) + list(lm.doubl_gaus().param_names))
    # counter used to add line per image analysed
    counter = 0

    temp_dir = os.path.join(save_dir, 'ImagesForDeletion')
    os.mkdir(temp_dir)

    for key in sorted(spots):
        print(f"Creating plots for {key}MeV Image")

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
        worksheet.write_column('J9', np.log10(spots[key].adjustedcropprofiles[1]))
        worksheet.write_column('K9', np.log10(spots[key].singlefitarray[spots[key].cropspotcentre[1]]))
        worksheet.write_column('L9', np.log10(spots[key].doublefitarray[spots[key].cropspotcentre[1]]))
        worksheet.write_column('M9', np.log10(spots[key].adjustedcropprofiles[3]))
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

# log_dir = "C:\\Users\\cgillies.UCLH\\Desktop\\LOGOS_Analysis\\Profiles_File_Key.xlsx"
log_dir = eg.fileopenbox('Select image acquisition log')
if not log_dir:
    print('No log selected, code will terminate')
    input('Press enter to close window')
    raise SystemExit

# acquiredfoldersdir = "C:\\Users\\cgillies.UCLH\\Desktop\\LOGOS_Analysis"
acquiredfoldersdir = eg.diropenbox('Select directory containing all acquired LOGOS folders')
if not acquiredfoldersdir:
    print('No acquisition directory selected, code will terminate')
    input('Press enter to close window')
    raise SystemExit

spots, ga, rs, dist = produce_spot_dict(log_dir, acquiredfoldersdir)

for key in spots:
    spots[key].create_fits()

plot_fits(spots, ga, rs, dist)
