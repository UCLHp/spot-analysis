import PySimpleGUI as sg

#
# """GUI returns data location, gantry and save location as dict
#
# Keys for returned dict: datadir, gantry, outputdir
# """
#
# sg.theme('BlueMono')
#
#
# # Define Layout
# layout = [
# [sg.Text("This is my test box")],
# [sg.Text('Data folder'), sg.In(key="Imagedir"), sg.FileBrowse()],
# [sg.Button("Analyse")]
# ]
# #
# window = sg.Window('Leeds Test Object Monthly Image Analysis', layout)
#
#
#
# while True:
#     event, values = window.read()
#     if event == "Analyse" and values["Imagedir"] != '':
#     # print(event)
#         print(values["Imagedir"])
#     # func(values["Imagedir"])
#
#
#
#     if event == sg.WIN_CLOSED:
#         break
#
#
#
# window.close()


def make_window(theme):
    sg.theme(theme)
    person_1 = [sg.Text('Investigator 1: '), sg.InputText(size = (5, 1), key = '-person1-')]
    person_2 = [sg.Text('Investigator 2: '), sg.InputText(size = (5, 1), key = '-person2-')]
    gantry = [sg.Text('Gantry: '), sg.InputText(size = (5, 1), key = '-gantry-')]
    gantry_angle = [sg.Text('Gantry angle: '), sg.InputText(size = (5, 1), key = '-gantry_angle-')]
    col_titles = [sg.Text('Proton energy (MeV)', size = (15, 1), justification = 'l'), sg.Text('Bmp picture locations', size = (20, 1), justification = 'l')]
    ent1 = [sg.Text('(1)'), sg.InputText(size = (10, 1), key = '-pro_en_1-'), sg.Text('@'), sg.InputText(key = '-bmp_loc_1-'), sg.FileBrowse()]
    ent2 = [sg.Text('(2)'), sg.InputText(size = (10, 1), key = '-pro_en_2-'), sg.Text('@'), sg.InputText(key = '-bmp_loc_2-'), sg.FileBrowse()]
    ent3 = [sg.Text('(3)'), sg.InputText(size = (10, 1), key = '-pro_en_3-'), sg.Text('@'), sg.InputText(key = '-bmp_loc_3-'), sg.FileBrowse()]
    ent4 = [sg.Text('(4)'), sg.InputText(size = (10, 1), key = '-pro_en_4-'), sg.Text('@'), sg.InputText(key = '-bmp_loc_4-'), sg.FileBrowse()]
    ent5 = [sg.Text('(5)'), sg.InputText(size = (10, 1), key = '-pro_en_5-'), sg.Text('@'), sg.InputText(key = '-bmp_loc_5-'), sg.FileBrowse()]
    comment = [sg.Text('Comments: '), sg.InputText(size = (50, 1), key = '-comment-')]
    button_submit = [sg.Button('Submit')]
    button_exit = [sg.Button('Exit')]

    layout = [[
             sg.Frame('Your spot measurements: ',
             [gantry + gantry_angle, person_1 + person_2, col_titles, ent1, ent2, ent3, ent4, ent5, comment, button_submit + button_exit])
             ]]

    window = sg.Window('please tell me about your spot measurements:', layout, finalize =True)
    # window.set_min_size(window.size)

    return window


def main():

    window = make_window(theme)


    while True:
        event, values = window.read()
        print(f'event: {event}')
        print(f'values: {values}')
        if event == 'Submit':
            en = []
            bmp_dir = []
            for i in range(1,6):
                str1 = '-pro_en_%s-' % str(i)
                str2 = '-bmp_loc_%s-' % str(i)
                if values[str1] not in en:
                    en.append(values[str1])
                else:
                    sg.popup('You have entred %s MeV twice! Please have a look at the Proton energy column!' % str(values[str1]))

                if values[str2] not in bmp_dir:
                    bmp_dir.append(values[str2])
                else:
                    sg.popup('Double check your bmp location column! Duplicated entry detected' )


            # print(f'>>> bmp_dir:{bmp_dir}')


            break
        window.close()
            # create the spotpattern object from five energies


            # check duplication and empty text box


            # check all energy and bmp entries !=0
        # print(event)

        # func(values["Imagedir"])



        if event == sg.WIN_CLOSED or event == 'Exit':
            break





    return




if __name__ == '__main__':
    theme = 'DefaultNoMoreNagging'
    # sg.theme('black')
    # sg.theme('dark red')
    # sg.theme('dark green 7')
    # sg.theme('DefaultNoMoreNagging')
    main()
