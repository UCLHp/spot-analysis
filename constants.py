
 # List of constants

# operators
operators = ('AB', 'AG', 'AGr', 'AK', 'AM', 'AP', 'AT', 'AW', 'CB', 'CG', 'KC', 'PI', 'RM', 'SC', 'SG', 'TNC', 'VMA', 'VR', 'NA')
gantries = ('1', '2', '3', '4')

# relate to the grid

pred_xrv4000 = {'Top-Top-Left': [-125, -175], 'Top-Top-Centre': [0, -175], 'Top-Top-Right': [125, -175], \
                'Top-Left': [-125, -125], 'Top-Centre':[0, -125], 'Top-Right':[125, -125], \
                'Left': [-125, 0], 'Centre':[0, 0], 'Right':[125, 0], \
                'Bottom-Left': [-125, 125], 'Bottom-Centre':[0, 125], 'Bottom-Right':[125, 125], \
                'Bottom-Bottom-Left': [-125, 175], 'Bottom-Bottom-Centre': [0, 175], 'Bottom-Bottom-Right': [125, 175]}

pred_xrv3000 = {'Top-Left': [-125, -125], 'Top-Centre':[0, -125], 'Top-Right':[125, -125], \
                'Left': [-125, 0], 'Centre':[0, 0], 'Right':[125, 0], \
                'Bottom-Left': [-125, 125], 'Bottom-Centre':[0, 125], 'Bottom-Right':[125, 125]}

# plan_loc_l = [-175, -125, 0, 125, 175]
# plan_loc_s = [-125,  0, 125]

# ## related to database

# #  Callum dummy database
DATABASE_DIR = r"C:\Users\cgillies.UCLH\Desktop\Spot_Grid_Testing.accdb"

# # Real proton database from Alison. We should push data to the backend of the database
# DATABASE_DIR = r"R:\AssetsDatabase_be.accdb"

# # Real proton database. back end.
# DATABASE_DIR = r"\\9.40.120.20\\rtassetBE\AssetsDatabase_be.accdb"

# ASSESS database front end password
# PWD = "Pr0ton5%"

# ASSESS database backend password
PWD = "JoNiSi"
# PWD = "TEST"

db_cols = ['date', 'gantry', 'energy', 'device', 'gantry_angle', 'spot', 'x-pos', 'y-pos', \
            'hor_r_grad', 'hor_l_grad', 'hor_fwhm', \
            'vert_r_grad', 'vert_l_grad', 'vert_fwhm', \
            'bltr_r_grad', 'bltr_l_grad', 'bltr_fwhm', \
            'tlbr_r_grad', 'tlbr_l_grad', 'tlbr_fwhm']

sigma = {70: 5.936, 100: 4.87, 150: 3.974, 200: 3.566, 240: 3.266}

expect_fwhm = {key: 2.355* value for key, value in sigma.items()}
