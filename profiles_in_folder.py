import easygui as eg
import os
import tps_profiles as tp

tps_dir = eg.diropenbox()

dir_list = [x[0] for x in os.walk(tps_dir)]
dir_list.pop(0)


for folder in dir_list:
    tp.produce_tps_profile_data(folder)
