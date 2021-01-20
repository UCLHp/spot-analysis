import logos_module as lm

import easygui as eg
import os
import tps_profiles as tp

tps_dir = eg.diropenbox()

dir_list = [x[0] for x in os.walk(tps_dir)]
dir_list.pop(0)


positions = []
for folder in dir_list:
    tif_image = [f for f in os.listdir(folder) if f.endswith('.tif')]
    spot_array = lm.image_to_array(tif_image[0], norm=True)
    X50, Y50 = lm.find_centre(spot_array, threshold=0.5)
    X90, Y90 = lm.find_centre(spot_array, threshold=0.9)
    positions.append(folder, X50, Y50, X90, Y90)

print(positions)
