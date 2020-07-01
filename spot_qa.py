import os
from logos_module import *
import easygui as eg
import pypyodbc
import test.test_version

<<<<<<< HEAD
def main():

    test.test_version.check_version()

    database_dir = ('\\\\krypton\\rtp-share$\\protons\\Work in Progress\\Christian'
                    '\\Database\\Proton\\Test FE - CB.accdb')

    conn = pypyodbc.connect(
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + database_dir + ';'
            )
    cursor = conn.cursor()

    # Produce list of energies for multchoicebox (taken from the Database)
    cursor.execute('select * from [ProtonEnergies]')
    energy_options = [row[0] for row in cursor.fetchall()]

    # Select acquired energies
    energies = eg.multchoicebox('Select Energies',
                                'Please select the energies that '
                                'have spot pattern image files', energy_options
                                )
    energies = sorted([float(i) for i in energies], reverse=True)
    print(f'Energies acquired: {energies}\n')

    # Select Operator from list in Database
    cursor.execute('select * from [Operators]')
    operators = [row[2] for row in cursor.fetchall()]
    operator = eg.choicebox('Who performed the measurements?',
                            'Operator',
                            operators)
    if not operator:
        eg.msgbox('Please re-run the code and select an Operator')
=======
database_dir = ('\\\\krypton\\rtp-share$\\protons\\Work in Progress\\Christian'
                '\\Database\\Proton\\Test FE - CB.accdb')

conn = pypyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + database_dir + ';'
        )
cursor = conn.cursor()

# Produce list of energies for multchoicebox (taken from the Database)
cursor.execute('select * from [ProtonEnergies]')
energy_options = [row[0] for row in cursor.fetchall()]

# Select acquired energies
energies = eg.multchoicebox('Select Energies',
                            'Please select the energies that '
                            'have spot pattern image files', energy_options
                            )
energies = sorted([float(i) for i in energies], reverse=True)
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
>>>>>>> DatabaseConnection
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
<<<<<<< HEAD
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

        image_loc = os.path.join(os.path.join(dir, foldername), '00001.bmp')


    ###############################################################################
    # Print Results and input to DB
    ###############################################################################

    sql = ('INSERT INTO [Spot Profile] ([ADate], [Operator], [Equipment], ' \
        '[MachineName], [GantryAngle], [Energy], [Spot Position], [X-Position], '\
        '[Y-Position], [Spot Size (Ave FWHM)], [Eccentricity], ' \
        '[Image File Location]) \nVALUES(?,?,?,?,?,?,?,?,?,?,?,?)')
    spot_pos = [    'top-left', 'top-centre', 'top-right',
                    'middle-left', 'middle-centre', 'middle-right',
                    'bottom-left', 'bottom-centre', 'bottom-right'  ]

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

        for y in range(1, (spot_properties[x].no_of_spots + 1)):
            subset = [  spot_properties[x].datetime,
                        operator,
                        'Logos3000',
                        gantry,
                        90,
                        x,
                        spot_pos[y-1],
                        spot_properties[x].spots_xy[y][0],
                        spot_properties[x].spots_xy[y][1],
                        spot_properties[x].spots_diameter[y],
                        spot_properties[x].spots_quality[y],
                        spot_properties[x].image_loc
                        ]

            cursor.execute(sql, subset)

    # Commit the changes to the database
    conn.commit()
if __name__ == '__main__':
    main()
=======
    output = os.path.join(os.path.join(dir, foldername), 'output.txt')
    spot_properties = {x: Output(output) for x in energies}

    image_loc = os.path.join(os.path.join(dir, foldername), '00001.bmp')


###############################################################################
# Print Results and input to DB
###############################################################################

sql = ('INSERT INTO [Spot Profile] ([ADate], [Operator], [Equipment], ' \
    '[MachineName], [GantryAngle], [Energy], [Spot Position], [X-Position], '\
    '[Y-Position], [Spot Size (Ave FWHM)], [Eccentricity], ' \
    '[Image File Location]) \nVALUES(?,?,?,?,?,?,?,?,?,?,?,?)')
spot_pos = [    'top-left', 'top-centre', 'top-right',
                'middle-left', 'middle-centre', 'middle-right',
                'bottom-left', 'bottom-centre', 'bottom-right'  ]

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

    for y in range(1, (spot_properties[x].no_of_spots + 1)):
        subset = [  spot_properties[x].datetime,
                    operator,
                    'Logos3000',
                    gantry,
                    90,
                    x,
                    spot_pos[y-1],
                    spot_properties[x].spots_xy[y][0],
                    spot_properties[x].spots_xy[y][1],
                    spot_properties[x].spots_diameter[y],
                    spot_properties[x].spots_quality[y],
                    spot_properties[x].image_loc
                    ]

        cursor.execute(sql, subset)

# Commit the changes to the database
conn.commit()
>>>>>>> DatabaseConnection
