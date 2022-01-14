import PySimpleGUI as sg
import os.path
import PIL.Image
import PIL.ImageDraw
import io
import base64

import spot_position_mod as spm
"""
    Demo for displaying any format of image file.

    Normally tkinter only wants PNG and GIF files.  This program uses PIL to convert files
    such as jpg files into a PNG format so that tkinter can use it.

    The key to the program is the function "convert_to_bytes" which takes a filename or a
    bytes object and converts (with optional resize) into a PNG formatted bytes object that
    can then be passed to an Image Element's update method.  This function can also optionally
    resize the image.

    Copyright 2020 PySimpleGUI.org
"""


def convert_to_bytes(file_or_bytes, resize=None, positions=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    if positions:
        draw = PIL.ImageDraw.Draw(img)
        for key in positions:
            print((positions[key][0],positions[key][1]))
            draw.ellipse((positions[key][0]-2, positions[key][1]-2,positions[key][0]+2, positions[key][1]+2 ), fill="black")

    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()


# --------------------------------- Define Layout ---------------------------------

# First the window layout...2 columns

left_col = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Text('Resize to'), sg.In(key='-W-', size=(5,1)), sg.In(key='-H-', size=(5,1))],
            [sg.Text('Threshold'), sg.In(key='-Th-', default_text='10', size=(5,1))],
            [sg.Text('Specificity'), sg.In(key='-Sp-', default_text='15', size=(5,1))],
            [sg.Text('Max Detection Size'), sg.In(key='-Si-', default_text='100', size=(5,1))],
            [sg.Text('Min distance between detected circles'), sg.In(key='-Mi-', default_text='20', size=(5,1))],
            [sg.Text('Extraction size'), sg.In(key='-Ex-', default_text='1.0', size=(5,1))]]


# For now will only show the name of the file that was chosen
images_col = [[sg.Text('You choose from the list:')],
              [sg.Text(size=(40,1), key='-TOUT-')],
              [sg.Image(key='-ORIG-')]]

# ----- Full layout -----
layout = [[sg.Column(left_col, element_justification='r'), sg.VSeperator(),sg.Column(images_col, element_justification='c')]]

# --------------------------------- Create Window ---------------------------------
window = sg.Window('Multiple Format Image Viewer', layout,resizable=True)

# ----- Run the Event Loop -----
# --------------------------------- Event Loop ---------------------------------
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp"))]
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
            window['-TOUT-'].update(filename)
            if values['-W-'] and values['-H-']:
                new_size = int(values['-W-']), int(values['-H-'])
            else:
                new_size = None

            spot_pattern = spm.SpotPattern(filename)
            positions = spot_pattern.output.spots_xy
            print(positions)

            # if len(positions) == 15:
            #     for key in positions:
            #         db_positions[key]
            # print(positions)
            center = [spot_pattern.activescript.AppXCenter, spot_pattern.activescript.AppYCenter]
            resol = [spot_pattern.activescript.CameraHRatio, spot_pattern.activescript.CameraVRatio]
            for key in positions:
                positions[key][0] = int((float(positions[key][0]) * float(resol[0])) + float(center[0]))
                positions[key][1] = int((float(positions[key][1]) * float(resol[1])) + float(center[1]))
                # if len(positions) == 15:
                #     positions[key][0] = -positions[key][0]
            # print(positions)
            window['-ORIG-'].update(data=convert_to_bytes(filename, resize=new_size, positions=positions))
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename
# --------------------------------- Close & Exit ---------------------------------
window.close()


# def main():
#
#
# if __name__ == '__main__':
#     main()
