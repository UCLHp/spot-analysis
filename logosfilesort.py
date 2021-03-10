import os
import pandas as pd
import shutil
import datetime
import easygui as eg

# xlsxfile = 'C:\\Users\\csmgi\\Desktop\\Work\\LocalLOGOSAnalysis.xlsx'
xlsxfile = eg.fileopenbox('Select excel file with image location details')

# logosdir = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\Test-Results\\Gantry 270'
logosdir = eg.diropenbox('Select folder destination for all spots')

# allfoldersdir = 'C:\\Users\\csmgi\\Desktop\\LOGOS Analysis_2'
allfoldersdir = eg.diropenbox('Select dir containing all capture folders')


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
        # print(full_data[10])
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


location_key = pd.read_excel(xlsxfile, engine='openpyxl')

# print(location_key)

location_key['Image'] = [str(int(i)).zfill(8) for i in location_key['Image']]
location_key['Collated Number'] = [str(int(i)).zfill(8) for i in location_key['Collated Number']]

datacheck = [["Collated Number", "Folder", "Image", "RS", "Distance", "Energy",
             "Width", "Height", "diameter"]]

copyfiles = input('Would you like to copy the folders? (y/n):')

while copyfiles.lower() not in ['y', 'n']:
    copyfiles = input("Please enter 'y' or 'n':")

for index, row in location_key.iterrows():
    folder = row['Folder']
    image_name = row['Image'] + '.tif'
    dist = row['Distance']
    RS = row['RS']
    new_image_name = row['Collated Number'] + '.tif'

    src = os.path.join(allfoldersdir, folder)
    print(f'Dist: {dist}', f'RS: {RS}', f"Energy: {row['Energy']}")
    output_file = Output(os.path.join(src, "output.txt"))

    src = os.path.join(src, image_name)

    image_num = int(row['Image'])
    line_to_write = list(row)
    line_to_write.append(output_file.spots_width[image_num])
    line_to_write.append(output_file.spots_height[image_num])
    line_to_write.append(output_file.spots_diameter[image_num])
    datacheck.append(line_to_write)

    dst = os.path.join(logosdir, f'RangeShifter_{RS}cm')

    if (dist) == 0:
        dist_folder = 'Distance_is0cm'
    if int(dist) < 0:
        dist_folder = f'Distance_m{abs(dist)}cm'
    if int(dist) > 0:
        dist_folder = f'Distance_p{dist}cm'

    dst = os.path.join(dst, dist_folder)
    dst = os.path.join(dst, new_image_name)

    if copyfiles.lower() == 'y':
        shutil.copyfile(src, dst)

df = pd.DataFrame(datacheck[1:], columns=datacheck[0])

saveresult = input('Would you like to save the results? (y/n):')
while saveresult.lower() not in ['y', 'n']:
    saveresult = input("Please enter 'y' or 'n'")
if saveresult == 'y':
    save_dir = eg.diropenbox('Select the save location')
    df.to_excel(os.path.join(save_dir, 'Data_QA_Summary.xlsx'))
