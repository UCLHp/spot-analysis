import os
import sys
import git
from logos_module import *
import xlsxwriter
import easygui as eg

cd = os.path.dirname(sys.argv[0])

g = git.cmd.Git()
blob = g.ls_remote("https://github.com/UCLHp/Spot_Analysis")

print(type(blob))

print(os.path.dirname(sys.argv[0]))
print(os.path.basename(sys.argv[0]))
# print(sha)

exit()
dir = eg.diropenbox(title='Please select location of tiff files')
file_list = os.listdir(dir)

if len(file_list) == 0:
    print('Selected directory is empty')
    print('Code Terminated')
    input('Press enter to close window')
    raise SystemExit


image_list = [f for f in os.listdir(dir) if f.endswith(('.tif', '.tiff',
                                                        '.jpg', '.bmp'))]













# import matplotlib.pyplot as plt
# from scipy import ndimage

# workbook = xlsxwrite.Workbook('SpotProfiles.xlsx')
# worksheet=workbook.add_worksheet('Sheet1')



# tiffile = fileopenbox(title='Please Select a Tif Image') #Asks user to select folder containing acquired tiff files
#
# workbook = xlsxwriter.Workbook('SpotProfiles.xlsx')
#
# worksheet=workbook.add_worksheet('Sheet1')
# Read = imread(tiffile)
# Data = np.array(Read).astype(np.float)
# XProfile, XpoptLOGshiftL, XpoptLOGshiftR, YProfile, YpoptLOGshiftL, YpoptLOGshiftR = SpotArrayToEquation(Data,Hor,Vert)
#
#     Xmodel=[]
#     for item in XProfile[0]:
#         if item<0:
#             Xmodel.append(10**funcLOGShift(item,*XpoptLOGshiftL))
#         if item>=0:
#             Xmodel.append(10**funcLOGShift(item,*XpoptLOGshiftR))
#     Ymodel=[]
#     for item in YProfile[0]:
#         if item<0:
#             Ymodel.append(10**funcLOGShift(item,*YpoptLOGshiftL))
#         if item>=0:
#             Ymodel.append(10**funcLOGShift(item,*YpoptLOGshiftR))
#     XmodelL=[]
#     for item in XProfile[0]:
#         XmodelL.append(10**funcLOGShift(item,*XpoptLOGshiftL))
#     XmodelR=[]
#     for item in XProfile[0]:
#         XmodelR.append(10**funcLOGShift(item,*XpoptLOGshiftR))
#     YmodelL=[]
#     for item in YProfile[0]:
#         YmodelL.append(10**funcLOGShift(item,*YpoptLOGshiftL))
#     YmodelR=[]
#     for item in YProfile[0]:
#         YmodelR.append(10**funcLOGShift(item,*YpoptLOGshiftR))
#
#     XProfile.append(Xmodel)
#     YProfile.append(Ymodel)
#     # XProfile.append(10**funcLOGShift(XProfile[0],*popt0))
#     Output = [XProfile[0],XProfile[1],XProfile[2],YProfile[0],YProfile[1],YProfile[2],XmodelL,XmodelR,YmodelL,YmodelR]
#     # Output = np.transpose(Output)
#
#     worksheet.write('B2', 'X Distance mm')
#     worksheet.write('C2', 'X Data')
#     worksheet.write('D2', 'X Model')
#     worksheet.write('E2', 'Y Distance mm')
#     worksheet.write('F2', 'Y Data')
#     worksheet.write('G2', 'Y Model')
#     worksheet.write('H2', 'X Model L')
#     worksheet.write('I2', 'X Model R')
#     worksheet.write('J2', 'Y Model L')
#     worksheet.write('K2', 'Y Model R')
#     row = 2
#
#     for item in Output[0]:
#         worksheet.write(row,1,item)
#         row +=1
#     row=2
#     for item in Output[1]:
#         worksheet.write(row,2,item)
#         row +=1
#     row=2
#     for item in Output[2]:
#         worksheet.write(row,3,item)
#         row +=1
#     row=2
#     for item in Output[3]:
#         worksheet.write(row,4,item)
#         row +=1
#     row=2
#     for item in Output[4]:
#         worksheet.write(row,5,item)
#         row +=1
#     row=2
#     for item in Output[5]:
#         worksheet.write(row,6,item)
#         row +=1
#     row=2
#     for item in Output[6]:
#         worksheet.write(row,7,item)
#         row +=1
#     row=2
#     for item in Output[7]:
#         worksheet.write(row,8,item)
#         row +=1
#     row=2
#     for item in Output[8]:
#         worksheet.write(row,9,item)
#         row +=1
#     row=2
#     for item in Output[9]:
#         worksheet.write(row,10,item)
#         row +=1
#     size1 = len(XProfile[0])
#     size2 = len(YProfile[0])
#
#
#     chart1 = workbook.add_chart({'type': 'scatter'})
#     chart1.add_series({
#         'name':       'Data',
#         'categories': "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$B$3:$B$"+str(11+size1)),
#         'values':     "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$C$3:$C$"+str(11+size1)),
#         'line': {'color':'red', 'width': 1,},
#         'marker': {'type':'none'},
#     })
#     chart1.add_series({
#         'name':       'Model',
#         'categories': "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$B$3:$B$"+str(11+size1)),
#         'values':     "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$D$3:$D$"+str(11+size1)),
#         'line': {'color':'blue', 'width': 1,},
#         'marker': {'type':'none'},
#     })
#     chart1.set_title ({'name': 'X Profile'})
#     chart1.set_x_axis({'name': 'X_Coordinate (mm)'})
#     chart1.set_y_axis({'name': 'Relative intensity'})
#     chart1.set_style(11)
#     chart1.set_size({'x_scale':1.55,'y_scale':1.6})
#     worksheet.insert_chart('M2', chart1)
#
#
#
#
#     chart2 = workbook.add_chart({'type': 'scatter'})
#     chart2.add_series({
#         'name':       'Data',
#         'categories': "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$E$3:$E$"+str(11+size2)),
#         'values':     "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$F$3:$F$"+str(11+size2)),
#         'line': {'color':'red', 'width': 1,},
#         'marker': {'type':'none'},
#     })
#     chart2.add_series({
#         'name':       'Model',
#         'categories': "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$E$3:$E$"+str(11+size2)),
#         'values':     "".join("="+str(os.path.splitext(os.path.basename(i))[0])+"!$G$3:$G$"+str(11+size2)),
#         'line': {'color':'blue', 'width': 1,},
#         'marker': {'type':'none'},
#     })
#     chart2.set_title ({'name': 'Y Profile'})
#     chart2.set_x_axis({'name': 'Y_Coordinate (mm)'})
#     chart2.set_y_axis({'name': 'Relative intensity'})
#     chart2.set_style(11)
#     chart2.set_size({'x_scale':1.55,'y_scale':1.6})
#     worksheet.insert_chart('M25', chart2)
#
# workbook.close()

# Read = imread(Tifs[3])
# Data = np.array(Read[500:700,700:900]).astype(np.float) # Convert to numpy array with floats

    # file = os.path.basename(filename) # Splits file into the location and:
    # name = float(os.path.splitext(file)[0]) # Extracts filename without extension (should be the energy)

# XProfile, XpoptLOGshiftL, XpoptLOGshiftR, YProfile, YpoptLOGshiftL, YpoptLOGshiftR = SpotArrayToEquation(Data,Hor,Vert)
# print(XpoptLOGshiftL)
# print(XpoptLOGshiftR)
# print(YpoptLOGshiftL)
# print(YpoptLOGshiftR)
