import os
# from tifffile import imread, imsave
from logos_module import *
# from scipy import ndimage
# from PDD_Module2 import *
import easygui as eg
# import pandas
# import matplotlib.pyplot as plt


energy_options = [x for x in list(range(70,245,5))+[244]] # Should link to database?

energies = eg.multchoicebox('Select Energies',
                            'Please select the energies that '
                            'have spot pattern image files', energy_options
                            )
energies = sorted([int(i) for i in energies], reverse=True)

dir = eg.diropenbox('Select Folders Containing Acquired Images '
                    'For All Acquired Energies')

if not len(energies)==len(os.listdir(dir)):
    eg.msgbox('Number of files in directory does not match number of Energies '
              'selected\nPlease re-run the program','File Count Error')


for foldername in sorted(os.listdir(dir)):
    # os.rename(os.path.join(dir,folder),os.path.join(dir,str(Energies[j])))
    # j+=1
    if os.path.isfile(os.path.join(os.path.join(dir,foldername),
                                   'activescript.txt'))==False:
        eg.msgbox(f"Folder {foldername} Doesn't contain the activescript "
                  "file required to calculate the image resolution")
        raise SystemExit
    if os.path.isfile(os.path.join(os.path.join(dir,foldername),
                                   'output.txt'))==False:
        eg.msgbox(f"Folder {foldername} Doesn't contain the output file "
                  "required for the spot data")
        raise SystemExit
    output = os.path.join(os.path.join(dir, foldername), 'output.txt')
    spot_properties = {x:Output(output) for x in energies}

print(spot_properties[energies[0]].center)
print(spot_properties[energies[0]].spots_xy)
print(spot_properties[energies[0]].spots_width)
print(spot_properties[energies[0]].spots_height)
print(spot_properties[energies[0]].spots_diameter)
print(spot_properties[energies[0]].spots_quality)



raise SystemExit
#     (x,y)=ReadActiveScriptLOGOS(os.path.join(os.path.join(dir,foldername),'activescript.txt')) # Takes resolution information from active script file
#     HorVals.append(x)
#     VertVals.append(y)
#
#     # with open(os.path.join(os.path.join(dir,foldername),'output.txt'), 'r') as f:
#     #     Placer = f.read().splitlines()
#     #     LOG_Output[j] = [i.split(",") for i in Placer]
#     with open(os.path.join(os.path.join(dir,foldername),'output.txt'), 'r') as f:
#         LOG_Output[Energies[j]] = [i.split(",") for i in f.read().splitlines()]
#
#     for file in os.listdir(os.path.join(dir,foldername)):
#         if file.endswith(('.tif','.tiff', 'bmp')): # Loops through all tif images in the directory
#             if Energies[j] not in SpotQAImages:
#                 SpotQAImages[Energies[j]] = [os.path.join(os.path.join(dir,foldername),file)] # Apends those filenames to the tif array
#             else:
#                 SpotQAImages[Energies[j]].append(os.path.join(os.path.join(dir,foldername),file))
#     if not Energies[j] in SpotQAImages: # Catch if a folder with no images is selected
#         easygui.msgbox("Folder "+ foldername+ " Doesn't contain an image\nPlease check the files in the QA folder")
#         exit()
#     # os.rename(os.path.join(dir,foldername),os.path.join(dir,str(Energies[j])))
#     j+=1
# if not len(LOG_Output.keys())==len(Energies):
#     print("Length not equal")
#
#     # print(LOG_Output)
#     # print("-\n-\n-\n-\n-")
#     # print(len(LOG_Output.keys()))
#     # print("-\n-\n-\n-\n-")
#     #
#     # Number_of_Spots = int(LOG_Output[j][2][1])
#     # print(Number_of_Spots)
# print(HorVals)
# print(VertVals)
# print(SpotQAImages)
# exit()
#
#
#
#
#
#     # Spot_Locs[j] = [i for i, s in enumerate(LOG_Output[j]) if 'X1Y1Z1' in s]
#     #
#     # SpotPosns=[]
#     # SpotWidth=[]
#     # SpotHeight=[]
#     # SpotRadial=[]
#     # SpotQuality=[]
#     #
#     # for i in range(0,Number_of_Spots):
#     #     SpotPosns.append([float(LOG_Output[Spot_Locs[i]][3]),float(LOG_Output[Spot_Locs[i]][4])])
#     #     SpotWidth.append([float(LOG_Output[Spot_Locs[i]+1][2])])
#     #     SpotHeight.append([float(LOG_Output[Spot_Locs[i]+2][2])])
#     #     SpotRadial.append([float(LOG_Output[Spot_Locs[i]+3][2])])
#     #     SpotQuality.append([float(LOG_Output[Spot_Locs[i]][-1])])
#
#
#
#
#
#
#
# ##############################
# # The LOGOS array is calibrated and has a set resolution in the x and y direction,
# # This resolution may change over different calibrations so should be read from the active script file
# # This loop also creates the "Spots" array which is a list of the Tif or bmp files in the selected folder.
# ##############################
#
#
# # for filename in os.listdir(dir): # Loop through each file in the directory
# #     print(filename)
# #     exit()
# #     file = os.path.basename(filename) # file is now filename without a path e.g. image.tif rather than C:/Users/Callum/image.tif
# #     if file.endswith(('.tif','.tiff', 'bmp')): # Loops through all tif images in the directory
# #         SpotQAImages.append(os.path.join(dir,filename)) # Apends those filenames to the tif array
# #     if file.endswith(".bmp"): # Loops through all tif images in the directory
# #         SpotQAImages.append(os.path.join(dir,filename)) # Apends those filenames to the tif array
# #     if file == 'activescript.txt': # Opens the "active script" file required for the resolution in x and y
# #         (Hor,Vert)=ReadActiveScriptLOGOS(os.path.join(dir,file)) # Takes resolution information from active script file
# #     if file == 'output.txt':
# #         with open(os.path.join(dir,filename), 'r') as f:
# #             LOG_Output = f.read().splitlines()
# #             LOG_Output = [i.split(",") for i in LOG_Output]
# # if not SpotQAImages: # Catch if a folder with no images is selected
# #     easygui.msgbox("Please select a folder that contains at least one spot image and re-run the code")
# #     exit()
# # if not Hor: # Catch if there is no activescript text file that contains details of the resolution
# #     easygui.msgbox("No activescript file found: Required to calculate the image resolution")
# #     exit()
# #
# #
# # Number_of_Spots = int(LOG_Output[2][1])
# #
# # Spot_Locs = [i for i, s in enumerate(LOG_Output) if 'X1Y1Z1' in s]
# #
# # SpotPosns=[]
# # SpotWidth=[]
# # SpotHeight=[]
# # SpotRadial=[]
# # SpotQuality=[]
# #
# # for i in range(0,Number_of_Spots):
# #     SpotPosns.append([float(LOG_Output[Spot_Locs[i]][3]),float(LOG_Output[Spot_Locs[i]][4])])
# #     SpotWidth.append([float(LOG_Output[Spot_Locs[i]+1][2])])
# #     SpotHeight.append([float(LOG_Output[Spot_Locs[i]+2][2])])
# #     SpotRadial.append([float(LOG_Output[Spot_Locs[i]+3][2])])
# #     SpotQuality.append([float(LOG_Output[Spot_Locs[i]][-1])])
#
#
#
#
# # exit()
# # ##############################
# # # In order to find the spots in the image, some parameters need to be optimised to find them.
# # # AllParams is an excel file containing all the default parameters. I haven't hard coded them becuase they may need to be changed
# # ##############################
# # AllParams = pandas.read_excel("C:/Users/cgillies/Desktop/Python_3/GIT Some/ReadLOGOS/Default_Spot_Detection.xlsx")
# #
# # ##############################
# #
# # Spot_Positions = {}
# # Cropped_Spots = {}
# # for i in SpotQAImages: # Cycle through each acquired QA image
# #     Energy = float(os.path.splitext(os.path.basename(i))[0]) # Extracts filename without extension (should be the energy)
# #     Params = AllParams[AllParams['Energy']==Energy] # Extracts the relevant parameters for the spot finding function from the "Parameters" array depending on the energies
# #     SpotPosns = FileNameToSpotPosition(i,Params) # Finds the coordinates of spots in the qa images based on Angelos' script
# #     Spot_Positions[Energy]=SpotPosns # labels each set with the respective energy
# #     # print(SpotPosns)
# #     Image = cv2.imread(i)
# #     # print(Image[0])
# #     j=1
# #     for coord in SpotPosns:
# #         # print(Image[x1:x2])
# #         # exit()
# #         print(j)
# #         Cropped_Spots.update({Energy:{j:{"Spot Image":Image[(coord[1]-60):(coord[1]+60),(coord[0]-60):(coord[0]+60)]}}})
# #         # if not Cropped_Spots[j].any():
# #         #     print((coord[1]-60),(coord[1]+60),(coord[0]-60),(coord[0]+60))
# #         # print(Energy)
# #         # print(Cropped_Spots[j])
# #         # plt.imshow(Cropped_Spots[j])
# #         # plt.show()
# #         j+=1
# # print(Cropped_Spots[100].keys())
# # # print(Spot_Positions)
# #
# #
# # exit()
