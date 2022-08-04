import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import constants as cs


# predicted spot (x,y) coordinates
pred_xrv4000 = cs.pred_xrv4000
pred_xrv3000 = cs.pred_xrv3000


markers = {240: 'o', 200: '<', 150:'s', 100:'X', 70:'^'}
colours = {240: '#FFA500', 200: '#FFD700', 150:'#7FFFD4', 100:'#90EE90', 70:'#7BC8F6'}

marker_bank = ['o', 'v', '8', '^', 's', '<', 'p', '>', 'P', 'd', 'X', 'D', 'H']

rainbow = ['#653700','#C79FEF',  '#650021', '#000000', '#A52A2A', \
           '#F97306', '#FFA500',  '#FAC205', '#DBB40C', '#9ACD32', \
           '#006400', '#04D8B2',  '#069AF3', '#7BC8F6', '#800080' , \
             ]


expect_fwhm = cs.expect_fwhm

#grid plot boundary
b = 2.5

def plot_spot_grid(df, device, tolerance):
    """ df = a dataframe with all spots in different Energy
        device = xrv3000 or xrv4000
        tolerance = int (1mm or 2mm)
    """

    title = "Absolute spot positions (%s mm tolerance)" % tolerance
    global b
    if tolerance ==1:
        b = 2.5
        title = "Relative spot positions (%s mm tolerance)" % tolerance


    # predicted spot grid
    if device == 'XRV-4000':
        pos = pred_xrv4000
        nrows = 5
        ncols = 3

    elif device == 'XRV-3000':
        pos = pred_xrv3000
        nrows = 3
        ncols = 3



    fig, axes = plt.subplots(nrows = nrows, ncols = ncols, figsize=(9,9))
    axes = axes.ravel()

    centre = df.loc[df['spot'] == 'Centre']
    centre = centre.set_index('energy')

    for i, p  in enumerate(list(pos.keys())):
        ndf = {}
        ndf = df.loc[df['spot'] == p]

        ndf = ndf.set_index('energy')
        # p_pos = pos[p]

        for e in ndf.index:
            if tolerance ==2:
                x = ndf.loc[e, 'x-pos']
                y = ndf.loc[e, 'y-pos']
            elif tolerance ==1:
                x = ndf.loc[e, 'x-pos'] - centre.loc[e, 'x-pos']
                y = ndf.loc[e, 'y-pos'] - centre.loc[e, 'y-pos']
            else:
                print(f'>> please check your tolerance input in your plot_spot_grid()!')

            cx = pos[p][0]
            cy = pos[p][1]
            axes[i].plot(x, y, color = colours[e], marker = markers[e],  fillstyle= 'none',linestyle = 'None', label = str(e))
            axes[i].set_aspect('equal')
            axes[i].add_patch(plt.Circle((cx, cy), radius = tolerance, color = '#F5F5DC', alpha = 0.5))
            axes[i].add_patch(plt.Rectangle((cx-tolerance, cy-tolerance), 2*tolerance, 2*tolerance, linewidth = 1, edgecolor='#DBB40C', facecolor = 'none' ))
            axes[i].set_title(p, fontsize=8, fontweight = 'bold')
            axes[i].tick_params(labelsize=8)
            axes[i].set_xlim(cx - b, cx + b)
            axes[i].set_ylim(cy - b, cy + b)
            axes[i].invert_yaxis()
        axes[i].plot(cx,cy, marker = '+', color = 'black', fillstyle= 'none', linestyle = 'None', label = 'planned')

    fig.suptitle(title)
    fig.supxlabel('x-pos (mm)')
    fig.supylabel('y-pos (mm)')
    plt.legend(loc='center left', bbox_to_anchor=(1.04, 0.5))
    fig.tight_layout()
    # plt.show()

    fig.savefig(title)
    plt.close(fig)

    return fig

def plot_shifts(df, device, tolerance):
    """ aims to plot the x,y shifts from the planned locations
        df = a dataframe with all spots in different Energy
        device = xrv3000 or xrv4000
        https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html#sphx-glr-gallery-lines-bars-and-markers-scatter-hist-py
        https://jakevdp.github.io/PythonDataScienceHandbook/04.08-multiple-subplots.html
    """
    title = "Absolute shifts (%s mm tolerance)" % str(tolerance)
    global b
    if tolerance ==1:
        b = 2.5
        title = "Relative shifts (%s mm tolerance)" % str(tolerance)

    # df = calc_shifts(df, device)

    # predicted spot grid
    # colors_loc = {} # pair the spot location with colours
    if device == 'XRV-4000':
        nrows = 5
        ncols = 3
        pos = pred_xrv4000
        # create the location-colour pairs
        # for i, n in enumerate(pos.keys()):
        #     colors_loc.update({n : rainbow[i]})


    elif device == 'XRV-3000':
        nrows = 3
        ncols = 3
        pos = pred_xrv3000
        # create the location-colour pairs
        # for i, n in enumerate(pos.keys()):
        #     colors_loc.update({n : rainbow[i]})

    fig, axes = plt.subplots(figsize=(12, 12))

    grid = plt.GridSpec(4, 4, hspace = 0.4, wspace = 0.4)
    ax_main = plt.subplot(grid[1:3, 1:3])
    ax_main.add_patch(plt.Circle((0, 0), radius = tolerance, color = '#D1B26F', alpha = 0.15))
    ax_main.add_patch(plt.Rectangle((-tolerance, -tolerance), 2*tolerance, 2*tolerance, linewidth = 1, edgecolor='#DBB40C', facecolor = 'none' ))
    ax_main.set_xlim([-b, b])
    ax_main.set_ylim([-b, b])
    ax_main.axhline(y = 0, xmin = -2.5, xmax = 2.5, linestyle = '--', color = '#929591', linewidth = 1 )
    ax_main.axvline(x = 0, ymin = -2.5, ymax = 2.5, linestyle = '--', color = '#929591', linewidth = 1)
    ax_main.set_aspect('equal')
    ax_main.invert_yaxis()

    ax_x = plt.subplot(grid[0, 1:3],  sharex = ax_main) # x-shifts
    ax_y = plt.subplot(grid[1:3, -1],  sharey = ax_main) # y-shifts



    # seaborn plot for the x, y- shifts
    if tolerance ==2:
        x_col = 'x-shift-abs'
        y_col = 'y-shift-abs'
    elif tolerance ==1:
        x_col = 'x-shift-rel'
        y_col = 'y-shift-rel'
    else:
        print(f'>> please check your tolerance input in the plot_shifts()!')


    smarkers = {}
    for key in markers.keys():
        smarkers.update({key: markers[key]})
    sns.scatterplot(data = df, x = x_col, y = y_col, hue = 'spot', style = 'energy', markers = smarkers, ax = ax_main)
    ax_main.legend(loc='upper left', bbox_to_anchor = (-0.1, -0.1) , ncol=4)


    ys = df[y_col].tolist()
    ax_y.hist(ys, bins = 15, histtype = 'stepfilled', orientation = 'horizontal', color='gray')
    ax_y.tick_params(axis="y")
    ax_y.set_xlabel('frequency')
    ax_y.set_ylabel('y-shifts (mm)')
    # ax_y.invert_yaxis()

    #x-shifts
    xs = df[x_col].tolist()
    ax_x.hist(xs, bins = 15, histtype = 'stepfilled', color='gray')
    ax_x.tick_params(axis="x")
    ax_x.set_ylabel('frequency')
    ax_x.set_xlabel('x-shifts (mm)')

    fig.suptitle(title)
    # plt.show()

    fig.savefig(title)
    plt.close(fig)

    return fig

def plot_shifts_by_energy(df, device, tolerance):
    """ aims to plot the x,y shifts from the planned locations
        df = a dataframe with all spots in different Energy
        device = xrv3000 or xrv4000
        https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html#sphx-glr-gallery-lines-bars-and-markers-scatter-hist-py
        https://jakevdp.github.io/PythonDataScienceHandbook/04.08-multiple-subplots.html
    """
    title = "Absolute shifts (%s mm tolerance) - by energy" % str(tolerance)
    global b
    if tolerance ==1:
        b = 2.5
        title = "Relative shifts (%s mm tolerance) - by energy" % str(tolerance)


    # df = calc_shifts(df, device)

    # predicted spot grid
    # colors_loc = {} # pair the spot location with colours
    if device == 'XRV-4000':
        nrows = 5
        ncols = 3
        pos = pred_xrv4000
        # create the location-colour pairs
        # for i, n in enumerate(pos.keys()):
        #     colors_loc.update({n : rainbow[i]})


    elif device == 'XRV-3000':
        nrows = 3
        ncols = 3
        pos = pred_xrv3000
        # create the location-colour pairs
        # for i, n in enumerate(pos.keys()):
        #     colors_loc.update({n : rainbow[i]})

    fig, axes = plt.subplots(figsize=(12, 12))

    grid = plt.GridSpec(4, 4, hspace = 0.4, wspace = 0.4)
    ax_main = plt.subplot(grid[1:3, 1:3])
    ax_main.add_patch(plt.Circle((0, 0), radius = tolerance, color = '#D1B26F', alpha = 0.15))
    ax_main.add_patch(plt.Rectangle((-tolerance, -tolerance), 2*tolerance, 2*tolerance, linewidth = 1, edgecolor='#DBB40C', facecolor = 'none' ))
    ax_main.set_xlim([-b, b])
    ax_main.set_ylim([-b, b])
    ax_main.axhline(y = 0, xmin = -2.5, xmax = 2.5, linestyle = '--', color = '#929591', linewidth = 1 )
    ax_main.axvline(x = 0, ymin = -2.5, ymax = 2.5, linestyle = '--', color = '#929591', linewidth = 1)
    ax_main.invert_yaxis()

    ax_x = plt.subplot(grid[0, 1:3],  sharex = ax_main) # x-shifts
    ax_y = plt.subplot(grid[1:3, -1],  sharey = ax_main) # y-shifts



    # seaborn plot for the x, y- shifts
    if tolerance ==2:
        x_col = 'x-shift-abs'
        y_col = 'y-shift-abs'
    elif tolerance ==1:
        x_col = 'x-shift-rel'
        y_col = 'y-shift-rel'
    else:
        print(f'>> please check your tolerance input in the plot_shifts()!')


    smarkers = {}
    for key in markers.keys():
        smarkers.update({key: markers[key]})
    sns.scatterplot(data = df, x = x_col, y = y_col, hue = 'energy', ax = ax_main)
    # sns.scatterplot(data = df, x = x_col, y = y_col, hue = 'energy', style = 'energy', markers = smarkers, ax = ax_main)
    ax_main.legend(loc='lower left', bbox_to_anchor = (-0.1, -0.3) , ncol=4)


    ys = df[y_col].tolist()
    ax_y.hist(ys, bins = 15, histtype = 'stepfilled', orientation = 'horizontal', color='gray')
    ax_y.tick_params(axis="y")
    ax_y.set_xlabel('frequency')
    ax_y.set_ylabel('y-shifts (mm)')
    # ax_y.invert_yaxis()

    #x-shifts
    xs = df[x_col].tolist()
    ax_x.hist(xs, bins = 15, histtype = 'stepfilled', color='gray')
    ax_x.tick_params(axis="x")
    ax_x.set_ylabel('frequency')
    ax_x.set_xlabel('x-shifts (mm)')

    fig.suptitle(title)
    # plt.show()

    fig.savefig(title)
    plt.close(fig)

    return fig

def plot_shifts_by_pos(df, device, tolerance):
    """ aims to plot the x,y shifts from the planned locations
        df = a dataframe with all spots in different Energy
        device = xrv3000 or xrv4000
        https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html#sphx-glr-gallery-lines-bars-and-markers-scatter-hist-py
        https://jakevdp.github.io/PythonDataScienceHandbook/04.08-multiple-subplots.html
    """
    title = "Absolute shifts (%s mm tolerance) - by position" % str(tolerance)
    global b
    if tolerance ==1:
        b = 2.5
        title = "Relative shifts (%s mm tolerance) - by position" % str(tolerance)


    if device == 'XRV-4000':
        nrows = 5
        ncols = 3
        pos = pred_xrv4000


    elif device == 'XRV-3000':
        nrows = 3
        ncols = 3
        pos = pred_xrv3000

    fig, axes = plt.subplots(figsize=(12, 12))

    grid = plt.GridSpec(4, 4, hspace = 0.4, wspace = 0.4)
    ax_main = plt.subplot(grid[1:3, 1:3])
    ax_main.add_patch(plt.Circle((0, 0), radius = tolerance, color = '#D1B26F', alpha = 0.15))
    ax_main.add_patch(plt.Rectangle((-tolerance, -tolerance), 2*tolerance, 2*tolerance, linewidth = 1, edgecolor='#DBB40C', facecolor = 'none' ))
    ax_main.set_xlim([-b, b])
    ax_main.set_ylim([-b, b])
    ax_main.axhline(y = 0, xmin = -2.5, xmax = 2.5, linestyle = '--', color = '#929591', linewidth = 1 )
    ax_main.axvline(x = 0, ymin = -2.5, ymax = 2.5, linestyle = '--', color = '#929591', linewidth = 1)
    ax_main.invert_yaxis()

    ax_x = plt.subplot(grid[0, 1:3],  sharex = ax_main) # x-shifts
    ax_y = plt.subplot(grid[1:3, -1],  sharey = ax_main) # y-shifts



    # seaborn plot for the x, y- shifts
    if tolerance ==2:
        x_col = 'x-shift-abs'
        y_col = 'y-shift-abs'
    elif tolerance ==1:
        x_col = 'x-shift-rel'
        y_col = 'y-shift-rel'
    else:
        print(f'>> please check your tolerance input in the plot_shifts()!')


    smarkers = {}
    for key in markers.keys():
        smarkers.update({key: markers[key]})
    sns.scatterplot(data = df, x = x_col, y = y_col, hue = 'spot', ax = ax_main)
    # sns.scatterplot(data = df, x = x_col, y = y_col, hue = 'energy', style = 'energy', markers = smarkers, ax = ax_main)
    ax_main.legend(loc='upper left', bbox_to_anchor = (-0.1, -0.1) , ncol=4)


    ys = df[y_col].tolist()
    ax_y.hist(ys, bins = 15, histtype = 'stepfilled', orientation = 'horizontal', color='gray')
    ax_y.tick_params(axis="y")
    ax_y.set_xlabel('frequency')
    ax_y.set_ylabel('y-shifts (mm)')
    # ax_y.invert_yaxis()

    #x-shifts
    xs = df[x_col].tolist()
    ax_x.hist(xs, bins = 15, histtype = 'stepfilled', color='gray')
    ax_x.tick_params(axis="x")
    ax_x.set_ylabel('frequency')
    ax_x.set_xlabel('x-shifts (mm)')

    fig.suptitle(title)
    # plt.show()

    fig.savefig(title)
    plt.close(fig)

    return fig

def plot_distribution(df):
    ''' Plot the distribution of the gradient ratio with a stripplot and volinplot'''

    title_gr = "gr_distribution"
    title_fwhm = "fwhm_distribution"

    # left, right gradients
    item_list = ['energy', 'spot',  'hor_gr', 'vert_gr', 'bltr_gr', 'tlbr_gr']
    tdf = df[item_list]
    ndf = df.melt(id_vars = item_list[0:2], value_vars = item_list[2:], var_name = 'profile_gr', value_name = 'gradient_ratio') # variable  = hor_gr... tlbr_gr || value = all values from variables


    fig, ax = plt.subplots(figsize = (16,9))

    # grid = plt.GridSpec(2, 2, width_ratios = (8,2), height_ratios = (5,5), hspace = 0.4, wspace = 0.4)
    # ax_pos = plt.subplot(grid[0, 0])
    grid = plt.GridSpec(2, 2, width_ratios = (5,5), height_ratios = (8,2), hspace = 0.4, wspace = 0.4)
    ax_pos = plt.subplot(grid[0, 0])
    # ax_pos_leg = plt.subplot(grid[0, 1])


    # by position
    sns.violinplot(x = 'energy', y = 'gradient_ratio', data = ndf, inner =None, color = '0.8', ax = ax_pos)
    sns.stripplot(x = 'energy', y = 'gradient_ratio', data = ndf, hue = 'spot', linewidth =1, palette = 'Spectral',  ax = ax_pos)
    # ax_pos.legend(bbox_to_anchor = (1, 1.0))
    ax_pos.legend(loc='upper left', bbox_to_anchor = (0.001, -0.1), ncol = 3)
    ax_pos.set_xlabel('Energy (MeV)')
    ax_pos.set_ylabel('Gradient ratio (a.u.)')
    # plt.tight_layout()

    # by profile
    # ax_pf = plt.subplot(grid[1, 0])
    ax_pf = plt.subplot(grid[0, 1])
    sns.violinplot(x = 'energy', y = 'gradient_ratio', data = ndf, inner =None, color = '0.8', ax = ax_pf)
    sns.stripplot(x = 'energy', y = 'gradient_ratio', data = ndf, hue = 'profile_gr', linewidth =1,  ax = ax_pf)
    # ax_pf.legend(loc='lower left', bbox_to_anchor = (1.005, 0.001))
    ax_pf.legend(loc='upper left', bbox_to_anchor = (0.001, -0.1))
    ax_pf.set_xlabel('Energy (MeV)')
    ax_pf.set_ylabel('Gradient ratio (a.u.)')

    # plt.show()
    fig.savefig(title_gr)
    plt.close(fig)


    # full-width half max distribution
    item_list = ['energy', 'spot',  'hor_fwhm', 'vert_fwhm', 'bltr_fwhm', 'tlbr_fwhm']
    tdf = df[item_list]
    ndf = df.melt(id_vars = item_list[0:2], value_vars = item_list[2:], var_name = 'profile_fwhm', value_name = 'fwhm') # variable  = hor_gr... tlbr_gr || value = all values from variables


    fig, ax = plt.subplots(figsize = (16,9))

    grid = plt.GridSpec(2, 2, width_ratios = (5,5), height_ratios = (8,2), hspace = 0.4, wspace = 0.4)
    ax_pos = plt.subplot(grid[0, 0])
    # ax_pos_leg = plt.subplot(grid[0, 1])


    # by position
    sns.violinplot(x = 'energy', y = 'fwhm', data = ndf, inner =None, color = '0.8', ax = ax_pos)
    sns.stripplot(x = 'energy', y = 'fwhm', data = ndf, hue = 'spot', linewidth =1, palette = 'Spectral', ax = ax_pos)
    ax_pos.legend(loc='upper left', bbox_to_anchor = (0.001, -0.1), ncol = 3)
    ax_pos.set_xlabel('Energy (MeV)')
    ax_pos.set_ylabel('FWHM (a.u.)')
    # plt.tight_layout()

    # by profile
    ax_pf = plt.subplot(grid[0, 1])
    sns.violinplot(x = 'energy', y = 'fwhm', data = ndf, inner =None, color = '0.8', ax = ax_pf)
    sns.stripplot(x = 'energy', y = 'fwhm', data = ndf, hue = 'profile_fwhm', linewidth =1,  ax = ax_pf)
    ax_pf.legend(loc='upper left', bbox_to_anchor = (0.005, -0.1))
    ax_pf.set_xlabel('Energy (MeV)')
    ax_pf.set_ylabel('FWHM (a.u.)')

    # plt.show()
    fig.savefig(title_fwhm)
    plt.close(fig)

    return fig

def plot_fwhm(df):
    ''' plot the mean fwhm for each profile and plot the beam model fwhm +/- 10% '''

    title = 'mean_fwhm_per_spot_per_energy'

    ndf = df[['energy', 'spot',  'hor_fwhm', 'vert_fwhm', 'bltr_fwhm', 'tlbr_fwhm']].copy()

    mfwhm = []
    for i in ndf.index:
        av = sum(ndf.iloc[i, 2:])/4
        mfwhm.append(av)

    ndf['mfwhm']= mfwhm
    pos = list(pd.unique(ndf['spot']))
    ndf = ndf.set_index('spot')

    sns_color = sns.color_palette('muted', len(pos))
    color_pos = {p:sns_color[i] for i, p in enumerate(pos)}

    exp_y = list(expect_fwhm.values())
    en = list(expect_fwhm.keys())


    yl = [y - 0.1*y for i, y in enumerate(exp_y)] # limit: 10% lower than y
    yu = [y + 0.1*y for i, y in enumerate(exp_y)]# limit: 10% higher than y


    fig, ax = plt.subplots(figsize = (8, 7))

    ax.plot(en, yl, linestyle = '--', color = '#E6DAA6' )
    ax.plot(en, yu, linestyle = '--', color = '#E6DAA6' )
    ax.fill_between( en, yl, yu, color = '#F5F5DC', alpha = 0.3 )

    for p in pos:
        pdf =  ndf.loc[p]
        x = pdf['energy'].tolist()
        y = pdf['mfwhm'].tolist()
        ax.plot(x , y , markersize = 5, color = color_pos[p], marker = 'o',  label = p, linestyle= '', markeredgecolor = '#F0FFFF')

    ax.plot( en, exp_y, 'k+', markersize = 10, label = 'expected FWHM')
    ax.set_xlabel('Proton energy (MeV)')
    ax.set_ylabel('FWHM (a.u.)')
    ax.legend(loc = 'upper left', bbox_to_anchor = (0.005, -0.1), ncol = 3)
    plt.tight_layout()
    plt.xticks(en, en)

    fig.savefig(title)
    plt.close(fig)


    return fig
