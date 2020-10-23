import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from astropy.modeling import fitting
import easygui as eg
import logos_module as lm

# Current issues:
# It is possible to have negative sigma values for double gaussian - need to add bounds
# A and B need to be linked to force one to be the primary



def produce_tps_profile_data():
    '''
    Function to produce spot profiles for entry into our TPS
    For a directory of acquired single spot tif files using the LOGOS4000
    A double 2D Gaussian is fitted (fat?) using the astropy library
    we then return the required profiles in the format required for the TPS
    '''

    DEFAULTDIR = 'C:/Users/csmgi/Desktop/Work/Coding/Test-Data/spot-analysis/VarietyOfSpots/'

    spot_dir = eg.diropenbox('Select directory containing spot images',
                             default = DEFAULTDIR)

    file_list = os.listdir(spot_dir)

    if 'activescript.txt' not in file_list:
        print('activescript.txt not found')
        print('This is required for the image resolution')
        print('Code Terminated')
        input('Press enter to close window')
        raise SystemExit
    else:
        print('activescript.txt file found\n')

    image_list = [f for f in os.listdir(spot_dir) if f.endswith(('.tif', '.tiff', 'jpg', '.bmp'))]

    image_list = sorted(image_list, key=lambda f: int(os.path.splitext(f)[0]))

    active_script = lm.ActiveScript(os.path.join(spot_dir,'activescript.txt'))
    resolution = [active_script.CameraHRatio, active_script.CameraVRatio]

    fit_p = fitting.LevMarLSQFitter()

    for key in image_list:
        spot_array = lm.image_to_array(os.path.join(spot_dir,key))
        centre = lm.find_centre(spot_array)
        my_model1 = lm.PSF(xo1 = centre[0]/resolution[0], yo1 = centre[1]/resolution[1])
        my_model2 = lm.twoD_Gaussian(xo1 = centre[0]/resolution[0], yo1 = centre[1]/resolution[1])
        y, x = np.mgrid[:len(spot_array[0]), :len(spot_array)]
        x = np.true_divide(x, resolution[0])
        y = np.true_divide(y, resolution[1])
        p1 = fit_p(my_model1, x, y, spot_array)
        p2 = fit_p(my_model2, x, y, spot_array)

        # print(f"The Sigma values for {key.split('.')[0]} are")
        # print(p.A)
        # print(p.sigma_x1)
        # print(p.sigma_y1)
        # print(p.sigma_x2)
        # print(p.sigma_y2)
        # print()

        # plt.imshow(spot_array)
        # plt.show()
        # plt.imshow(p(x,y))
        # plt.show()
        # plt.imshow(np.absolute(p(x,y) - spot_array))
        # plt.show()


        plt.plot(spot_array[centre[1]])
        plt.plot(p1(x,y)[centre[1]])
        plt.plot(p2(x,y)[centre[1]])
        plt.title(f'{key}')
        plt.show()


if __name__ == '__main__':
    produce_tps_profile_data()
