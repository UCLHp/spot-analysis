import os
import datetime
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askdirectory


class Output:
    '''
    The Output class will create an object that contains the information
    held in the output.txt file generated by the LOGOS software when
    capturing images
    '''
    def __init__(self, textfile):
        file = open(textfile, 'r')
        full_data = []
        for line in file:
            full_data.append([x.lstrip().rstrip() for x in line.split(',')])
        print(full_data[10])
        if full_data[10] == ['']:
            self.no_of_spots = int(full_data[-6][0])
        else:
            self.no_of_spots = int(full_data[-5][0])
        self.full_data = full_data
        date = full_data[0][3]
        self.datetime = datetime.datetime.strptime(date, '%H:%M:%S %m/%d/%Y')
        self.center = [float(full_data[0][5]), float(full_data[0][6])]
        self.spots_xy = {}
        self.spots_xy_rel = {}
        self.spots_width = {}
        self.spots_height = {}
        self.spots_diameter = {}
        self.spots_quality = {}
        for i in range(1, 1+self.no_of_spots):
            row = [full_data.index(x) for x in full_data if x[0] == str(i)][0]
            self.spots_xy[i] = [self.center[0] - float(full_data[row][3]),
                                self.center[1] - float(full_data[row][4])]
            self.spots_xy_rel[i] = [float(full_data[row][3]),
                                    float(full_data[row][4])]
            self.spots_width[i] = float(full_data[row][19])
            self.spots_height[i] = float(full_data[row][23])
            self.spots_diameter[i] = float(full_data[row][25])
            self.spots_quality[i] = float(full_data[row][27])


logosdir = askdirectory(title='Please select location of acquired files\n')

if not logosdir:
    print('No directory selected:')
    print('Code terminated')
    input('Press enter to close window')
    raise SystemExit

file_list = os.listdir(logosdir)

if 'output.txt' not in file_list:
    print('output.tx file not found')
    print('This is required to analyse images')
    print('Code Terminated')
    input('Press enter to close window')
    raise SystemExit
else:
    print('output.txt file found\n')

output_file = Output(os.path.join(logosdir, 'output.txt'))

widths = list(output_file.spots_width.values())
heights = list(output_file.spots_height.values())
diameters = list(output_file.spots_diameter.values())
qualities = list(output_file.spots_quality.values())

print('widths, heights, diameters, qualities\n')
for i in range(len(widths)):
    print(widths[i], heights[i], diameters[i], qualities[i])
# print('\nheights\n')
# for i in heights:
#     print(i)
# print('\ndiameters\n')
# for i in diameters:
#     print(i)
# print('\nqualities\n')
# for i in qualities:
#     print(i)


fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('FWHMs')
ax1.plot(heights, 'bx', label='Heights')
ax1.plot(widths, 'rx', label='Widths')
ax1.plot(diameters, 'gx', label='average FWHM every 5 degrees')
ax1.legend(loc="upper left")

ax2.plot(list(output_file.spots_quality.values()),
         label='quality as defined by LOGOS')
ax2.legend(loc="upper left")

plt.show()