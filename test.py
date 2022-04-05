import pandas as pd
import os
import numpy as np
import easygui as eg


import matplotlib.pyplot as plt
import PySimpleGUI as sg

import figures as fg
import spot_position_mod as spm
import spot_position_func as spf
import database as db
import constants as cs
import report as rp



def make_window_after_reviewing_data(theme):
    sg.theme(theme)
    text = [sg.Text('Please review your spot position data! If you have any comments, please write it down below.')]
    comment2 = [sg.Text('Comments: '), sg.InputText(size = (50, 1), key = '-comment2-')]

    # buttons
    button_submit = [sg.Button('Submit')]
    button_cancel = [sg.Button('Cancel')]

    layout = [ text, comment2, button_submit + button_cancel]

    window = sg.Window('Data reviewing:' , layout, finalize = True)

    return window




if __name__ == '__main__':
    theme = 'DefaultNoMoreNagging'

    window2 = make_window_after_reviewing_data(theme)
    event2, values2 = window2.read()


    print(f'event2: {event2}')
    print(f'values2 : {values2}')
