import logos_module as lm

import statistics as stats
import easygui as eg
import os
import tps_profiles as tp
import numpy as np

def pixel_is_hot(myarray, x, y):
    a = float(myarray[x,y])
    b = float(myarray[x+1,y])
    c = float(myarray[x-1,y])
    d = float(myarray[x,y+1])
    e = float(myarray[x,y-1])
    f = float(myarray[x+1,y+1])
    g = float(myarray[x+1,y-1])
    h = float(myarray[x-1,y+1])
    i = float(myarray[x-1,y-1])
    mean_pix = stats.mean([a, b, c, d, e, f, g, h, i])
    std_pix = stats.stdev([a, b, c, d, e, f, g, h, i])
    return a > mean_pix+(2*std_pix)


tps_dir = eg.diropenbox()

dir_list = [x[0] for x in os.walk(tps_dir)]
dir_list.pop(0)


positions = []
for folder in dir_list:
    tif_image = [f for f in os.listdir(folder) if f.endswith('.tif')]
    if not tif_image:
        positions.append('No Image acquired')
        continue
    tif_path = os.path.join(folder, tif_image[0])
    spot_array = lm.image_to_array(tif_path, norm=False)

    coord = [np.where(spot_array==np.amax(spot_array))[0], np.where(spot_array==np.amax(spot_array))[1]]

    while pixel_is_hot(spot_array, coord[0], coord[1]):
        print(pixel_is_hot(spot_array, coord[0], coord[1]))
        print(spot_array[coord[0], coord[1]])
        spot_array[coord[0], coord[1]] = 0
        coord = [np.where(spot_array==np.amax(spot_array))[0], np.where(spot_array==np.amax(spot_array))[1]]
        print(coord[0][0])
        print('pixel changed')

    X50, Y50 = lm.find_centre(spot_array, threshold=0.5)
    X90, Y90 = lm.find_centre(spot_array, threshold=0.9)
    positions.append([folder, X50, Y50, X90, Y90])
    print(f'Completed {folder}')

print(positions)



# import easygui as eg
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import cm
# from PIL import Image
# import statistics as stats
#
#
# def Plot3D(Data):
#     fig = plt.figure()  # create the pop up window for the plot
#     ax = fig.gca(projection='3d')  # command to change axes properties
#
#     X = np.asarray(range(0, Data.shape[1]))  # create 0-length axis
#     Y = np.asarray(range(0, Data.shape[0]))  # create 0-height axis
#
#     X, Y = np.meshgrid(X, Y)  # creates coordinates required to plot
#
#     surf = ax.plot_surface(X, Y, Data, cmap=cm.coolwarm, linewidth=0, antialiased=False)  # creates plot
#
#     fig.colorbar(surf, shrink=0.5, aspect=5)  # makes plot look pretty
#     plt.show()
#
#
# def csv_to_array(location):
#     spotdata = [x.split(',') for x in open(location).readlines()]
#     new_array = spotdata[5:-5]
#     count = 0
#     for line in new_array:
#         new_array[count] = [c.replace(" ", "") for c in line]
#         count += 1
#         return np.asarray(new_array).astype(float)
#
#
# def image_to_array(my_file, norm=False):
#     '''
#     Takes a file path as an input and reads it using the PIL Image library and
#     then returns the data as a numpy array.
#     Will normalise the array to a maximum of 1 if norm set to True
#     '''
#     my_image = Image.open(my_file)  # Image is a class within the PIL library
#     my_array = np.array(my_image)
#     my_array = np.rot90(my_array, 1)  # Images are 90deg off from expected
#     if norm:
#         my_array = np.true_divide(my_array, np.amax(my_array))
#     return my_array
#
#
#
#
# DIR1 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0001\\00000001.csv'
# DIR2 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0002\\00000001.csv'
# DIR3 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0003\\00000001.csv'
# DIR4 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0004\\00000001.csv'
# DIR7 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0007\\00000001.csv'
#
# IMG1 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0001\\00000001.tif'
# IMG2 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0002\\00000001.tif'
# IMG3 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0003\\00000001.tif'
# IMG4 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0004\\00000001.tif'
# IMG7 = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Data\\LOGOS\\Spot_Shifts\\2021_0115_0007\\00000001.tif'
#
# F1 = csv_to_array(DIR1)
# F2 = csv_to_array(DIR2)
# F3 = csv_to_array(DIR3)
# F4 = csv_to_array(DIR4)
# F7 = csv_to_array(DIR7)
#
# IM1 = image_to_array(eg.fileopenbox())
# IM2 = image_to_array(IMG2)
# IM3 = image_to_array(IMG3)
# IM4 = image_to_array(IMG4)
# IM7 = image_to_array(IMG7)
#
#
# X50, Y50 = lm.find_centre(IM1, threshold=0.5)
# X90, Y90 = lm.find_centre(IM1, threshold=0.9)
# print(X50, Y50, X90, Y90)
#
# coord = [np.where(IM1==np.amax(IM1))[0], np.where(IM1==np.amax(IM1))[1]]
#
# while pixel_is_hot(IM1, coord[0], coord[1]):
#     print(pixel_is_hot(IM1, coord[0], coord[1]))
#     print(IM1[coord[0], coord[1]])
#     IM1[coord[0], coord[1]] = int(IM1[coord[0], coord[1]])//2
#     coord = [np.where(IM1==np.amax(IM1))[0], np.where(IM1==np.amax(IM1))[1]]
#     print('pixel changed')
#
#
# X50, Y50 = lm.find_centre(IM1, threshold=0.5)
# X90, Y90 = lm.find_centre(IM1, threshold=0.9)
# print(X50, Y50, X90, Y90)
#
#
