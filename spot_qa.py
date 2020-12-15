import os
from logos_module import *
import easygui as eg
import pypyodbc
# import test.test_version

database_dir = 'C:\\Users\\csmgi\\Desktop\\Work\\Coding\\CatPhan\\AssetsDatabaseInProgress.accdb'

conn = pypyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + database_dir + ';'
        )
cursor = conn.cursor()

# Produce list of energies for multchoicebox - could be linked to Database?
energy_options = [x for x in list(range(70, 245, 5))+[244]]

# Select acquired energies
energies = eg.multchoicebox('Select Energies',
                            'Please select the energies that '
                            'have spot pattern image files', energy_options
                            )
energies = sorted([int(i) for i in energies], reverse=True)
print(f'Energies acquired: {energies}\n')

# Select Operator from list in Database
cursor.execute('select * from [Operators]')
operators = [row[2] for row in cursor.fetchall()]
operator = eg.choicebox('Who performed the measurements?',
                        'Operator',
                        operators)
if not operator:
    eg.msgbox('Please re-run the code and select an Operator')
    raise SystemExit
print(f'Operator = {operator}\n')

# Select Gantry from list in Database
cursor.execute('select * from [MachinesQuery]')
machines = [row[0] for row in cursor.fetchall()]
gantry = eg.choicebox('Which room were the measurements performed in?',
                      'Gantry',
                      machines)
if not gantry:
    eg.msgbox('Please re-run the code and select a room')
    raise SystemExit
print(f'Gantry = {gantry}\n')

# User selects directory containing all acquired spot grid energies
dir = eg.diropenbox('Select Folders Containing Acquired Images '
                    'For All Acquired Energies')

# Check to ensure number of energies defined matches the number of images
if not len(energies) == len(os.listdir(dir)):
    eg.msgbox('Number of files in directory does not match number of Energies '
              'selected\nPlease re-run the program', 'File Count Error')
    raise SystemExit

if not dir:
    eg.msgbox('Please re-run the code and select a folder containing the data'
              ' to be analysed', title='Folder Selection Error')
    raise SystemExit

# Loop to populate output dictionary from LOGOS output files
for foldername in sorted(os.listdir(dir)):
    if not os.path.isfile(os.path.join(os.path.join(dir, foldername),
                                       'activescript.txt')):
        eg.msgbox(f"Folder {foldername} Doesn't contain the activescript "
                  "file required to calculate the image resolution")
        raise SystemExit
    if not os.path.isfile(os.path.join(os.path.join(dir, foldername),
                                       'output.txt')):
        eg.msgbox(f"Folder {foldername} Doesn't contain the output file "
                  "required for the spot data")
        raise SystemExit
    output = os.path.join(os.path.join(dir, foldername), 'output.txt')
    spot_properties = {x: Output(output) for x in energies}

###############################################################################
# Print Results - will input to DB once table is created
###############################################################################

print(f'Operator was {operator}\n')
print(f'Images acquired on {gantry}\n')
for x in energies:
    print(f"Results for {x}MeV Spots:\n")
    print('Center:')
    print(spot_properties[x].center)
    print('Spot Positions:')
    print(spot_properties[x].spots_xy)
    print('Spot Width:')
    print(spot_properties[x].spots_width)
    print('Spot Height:')
    print(spot_properties[x].spots_height)
    print('Averaged Spot Diameter:')
    print(spot_properties[x].spots_diameter)
    print('Spot Circularity:')
    print(spot_properties[x].spots_quality)
    print()
