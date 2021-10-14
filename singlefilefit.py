from os import listdir
from os.path import join
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


def find_image_type(folder_path):
    '''Return the image type acquired

    LOGOS images can be acquired as 8bit bmp images or 16 bit tif images
    this function looks to see which extension is present in the file list of
    the selected folder
    '''
    file_contents = listdir(folder_path)
    if any('bmp' in filename for filename in file_contents):
        img_type = '.bmp'
    else:
        img_type = '.tif'
    return img_type


class SingleSpotSet:
    '''
    Class to group a single acquisition folder from the XRV4000/3000
    '''
    def __init__(self, image_dir, ga='', rs='', dist=''):
        self.activescript = lm.ActiveScript(join(image_dir, 'activescript.txt'))
        self.im_type = find_image_type(image_dir)
        self.im_list = [im for im in listdir(image_dir) if im.endswith(self.im_type)]

    def __str__(self):
        return (f'This set of {len(self.im_list)} spots was acquired using '
                f'the {self.activescript.device} in {self.im_type} format '
                f'\n The set was acquired at gantry angle {ga} with range'
                f' shifter {rs} at a distance of {dist}')


    def adddetails(self):
        self.ga = eg.integerbox(msg='Gantry Angle',
                                     title='Select angle of acquisition',
                                     lowerbound=0,
                                     upperbound=360
                                     )

        self.rs = eg.choicebox('Please select Range Shifter',
                          'RS', ['None', '2cm', '3cm', '5cm']
                          )

        self.dist = eg.integerbox(msg='Distance',
                               title='Enter the distance from iso',
                               lowerbound=-41,
                               upperbound=41
                               )

        print('Pulling spot data...')
        self.spotlist = [lm.Spot(join(self.image_dir, i),
                         ga=self.ga, rs=self.rs, dist=self.dist) for i in self.im_list]

        def fit(self):
            for spot in self.spotlist:
                spot.create_fits()


def fit_file(folder_path):
    activescript = lm.ActiveScript(join(folder_path,
                                   'activescript.txt')
                                   )
    im_type = find_image_type(folder_path)
    print(im_type)
    im_list = [im for im in listdir(folder_path) if im.endswith(im_type)]
    for spot in im_list:
        im_array = lm.image_to_array(join(folder_path, spot))
        if activescript.device == '4000':
            img_array = np.rot90(im_array, 1)

        crop_spot = lm.cropspot(img_array, lm.find_spot(img_array), cutoff=0.5,
                                growby=4
                                )
    print('success')


test = SingleSpotSet("C:\\Users\\cgillies.UCLH\\Desktop\\SORT_OR_DELETE\\LOGOS_Analysis\\2021_0316_0007")
# print(test)
test.adddetails()

# if __name__ == '__main__':
    #fit_file(eg.diropenbox())
