import os

import easygui as eg

'''
This script is designed to quickly check the values of spot grid positions
on set to check values are within tolerance before transfering to the database
'''

SPOTSIN3000 = {1: [-125, -125], 2: [0, -125], 3: [125, -125],
               4: [-125, 0], 5: [0, 0], 6: [125, 0],
               7: [-125, 125], 8: [0,125], 9: [125, 125]
               }

SPOTSIN4000 = {1: [-175, -125], 2: [-125, -125], 3: [0, -125], 4: [125, -125], 5: [175, -125],
               6: [-175, 0], 7: [-125, 0], 8: [0, 0], 9: [125, 0], 10: [175, 0],
               11: [-175, 125], 12: [-125, 125], 13: [0, 125], 14: [125, 125], 15: [175, 125]
               }

class ActiveScript:
    def __init__(self, image_dir):
        actscr_loc = os.path.join(os.path.dirname(image_dir),
                                  'activescript.txt')
        for line in open(actscr_loc, 'r'):
            if line.startswith('TextPath'):
                if '3' in line:
                    self.device = '3000'
                elif '4' in line:
                    self.device = '4000'
                else:
                    self.device = 'Unknown'

class Output:
    '''
    The Output class will create an object that contains the information
    held in the output.txt file generated by the LOGOS software when
    capturing images
    '''
    def __init__(self, image_dir):
        textfile = os.path.join(os.path.dirname(image_dir),
                                  'output.txt')
        file = open(textfile, 'r')
        full_data = []
        for line in file:
            full_data.append([x.lstrip().rstrip() for x in line.split(',')])
            if line.startswith('Beamspots found'):
                no_of_spots = int(line[18:])
        self.no_of_spots = no_of_spots
        self.spots_xy = {}

        for i in range(1, 1+self.no_of_spots):
            row = [full_data.index(x) for x in full_data if x[0] == str(i)][0]
            self.spots_xy[i] = [full_data[row][3],full_data[row][4]]

class SpotPattern:
    '''Class to define spot pattern images acquired using the flat LOGOS panels
    '''
    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            print('No image selected, code will terminate')
            input('Press any key to continue')
            raise SystemExit

        image_dir = os.path.dirname(image_path)

        if not os.path.isfile(os.path.join(image_dir, 'activescript.txt')):
            print('No active script detected for this spot pattern')
            input('Press any key to continue')
            raise SystemExit

        self.path = image_path
        self.activescriptpath = os.path.join(image_dir, 'activescript.txt')
        self.activescript = ActiveScript(self.activescriptpath)
        self.outputpath = os.path.join(image_dir, 'output.txt')
        self.output = Output(self.outputpath)


def main():
    image_loc = eg.fileopenbox(msg='Please select acquisition image',
                               title='Folder selection',
                               default='*.bmp',
                               filetypes=['*.bmp', '*.tif', 'Image files'])

    if not image_loc:
        input('No file selected, code will terminate. Press enter')
        raise SystemExit

    grid = SpotPattern(image_loc)

    # Convert position values in output file from strings to floats
    for k, v in grid.output.spots_xy.items():
        grid.output.spots_xy[k] = [float(i) for i in v]

    grid.absolute_positions = {}
    grid.relative_positions = {}

    if grid.activescript.device == '4000':
        # Subtract expected positions from those measured by device
        # Then create relative positions by subtracting the central point
        for key in SPOTSIN4000:
            grid.absolute_positions[key] = [grid.output.spots_xy[key][0] - SPOTSIN4000[key][0], grid.output.spots_xy[key][1] - SPOTSIN4000[key][1]]
            grid.relative_positions[key] = [grid.absolute_positions[key][0] - grid.output.spots_xy[8][0], grid.absolute_positions[key][1] - grid.output.spots_xy[8][1]]
    if grid.activescript.device == '3000':
        for key in SPOTSIN3000:
            grid.absolute_positions[key] = [grid.output.spots_xy[key][0] - SPOTSIN3000[key][0], grid.output.spots_xy[key][1] - SPOTSIN3000[key][1]]
            grid.relative_positions[key] = [grid.absolute_positions[key][0] - grid.output.spots_xy[5][0], grid.absolute_positions[key][1] - grid.output.spots_xy[5][1]]

    print('Absolute Spot Positions, tolerance 2mm')
    for a in grid.absolute_positions:
        print(grid.absolute_positions[a])
    print()
    print()
    print('Relative Spot Positions, tolerance 1mm')
    for a in grid.relative_positions:
        print(grid.relative_positions[a])

if __name__ == '__main__':
    main()
    input('Press enter to continue')
