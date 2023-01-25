import json
# import datetime
import pandas as pd
import os

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, TableStyle, Table, PageBreak, Frame
from  reportlab.platypus.flowables import Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm

from reportlab.lib import utils

import constants as cs

width, height = letter

# expected FWHM from beam model data
exp_fwhm = cs.expect_fwhm


# doc = SimpleDocTemplate("report.pdf",pagesize=letter)

# class to rotate the image
# when you rotate the image, you also rotate the origin of the image.
# class RotatedImage(Image):
#     def wrap(self,availWidth,availHeight):
#          h, w = Image.wrap(self,availHeight,availWidth)
#          return w, h
#     def draw(self):
#         self.canv.rotate(90)
#         self.translate(width/5 *cm, height/5*cm)
#         Image.draw(self )


def pass_fail(xs, ys, t, e, p):
    ''' return a list of ['energy', 'spot position', 'pass/fail']
    xs = x-shift-abs  // x-shift-rel
    ys = y-shift-abs  // y-shift-rel
    t = t-abs  // t-rel
    e = Energy
    p = spot position

    abs_tab and rel_tab  =  a nested list containing the spot position and energy information if it exceeds the tolerance.
    mspot = a nested list containing the spot position and energy in a nested list.
    '''

    if xs < t and xs > -t:
        if ys < t and ys > -t:
            str = [p, e, 'All Passed']
        else:
            str = [p, e, 'OOT (y)']

    else:
        if ys < t and ys > -t:
            str = [p, e, 'OOT (x)']
        else:
            str = [p, e, 'Both OOT']

    return str

def make_table(df, aEn):
    ''' df is the dataframe output as the result.xlsx files
        aEn is all energy input in the first Gui
        to make the summary table in the report'''

    ndf = df.groupby('spot')
    ndf = df.set_index('spot')

    t_rel = 1 # relative tolerance
    t_abs = 2 # absolute tolerance

    pos = list(pd.unique(df['spot'])) # spot position detected

    # catch any positions that do not detect a spot for all energy layers
    device = str(df['device'][0])

    if device == 'XRV-4000':
        exp_pos = list(cs.pred_xrv4000.keys())
    elif device == 'XRV-3000':
        exp_pos = list(cs.pred_xrv3000.keys())

    mspot = [] # find the missing spot location and its energy
    for p in exp_pos:
        if p not in pos:
            for e in aEn:
                mspot.append([p, str(e)])

    data = []
    remarks = {}
    # header = ['Positions', 'Absolute shifts within 2 mm', 'Relative shifts within 1 mm']
    header = ['Positions', 'Absolute shifts within 2 mm', 'Relative shifts within 1 mm', 'mFWHM']
    data.append(header)

    rel = []
    abs = []

    mfwhm = [] # record any OFT FWHM per spot position per energy
    for p in pos:
        cdf = ndf.loc[p]
        en = list(pd.unique(cdf['energy']))

        abs_fe = []
        rel_fe = []

        mfwhm_fe = [] # record mfwhm fe
        no_dim = cdf.ndim

        # en_pos = cdf['energy'].tolist()
        en_pos = []
        if no_dim == 2: # has more than two energies detected at the same position
            en_pos = cdf['energy'].tolist()
        if no_dim == 1: # has only one energy detected at the same position. need to change from dataframe to pd.series
            en_pos.append(cdf['energy'])
            cdf = cdf.to_frame().T

        # missing energy per spot location if any
        for e in aEn:
            if int(e) not in en:
                mspot.append([p, str(e)])

        for e in en_pos:
            # if no_dim ==2:
            #absolute shifts
            xs = cdf.loc[cdf['energy'] == e, 'x-shift-abs'].iloc[0]
            ys = cdf.loc[cdf['energy'] == e, 'y-shift-abs'].iloc[0]

            # relative shifts
            xsr = cdf.loc[cdf['energy'] == e, 'x-shift-rel'].iloc[0]
            ysr = cdf.loc[cdf['energy'] == e, 'y-shift-rel'].iloc[0]

            abs_res = pass_fail(xs, ys, t_abs, e, p)
            rel_res = pass_fail(xsr, ysr, t_rel, e, p)

            # find the fail (x,y)
            if 'Both OOT' in abs_res[2]:
                str1 = 'x: %s, y: %s ' % (str(round(xs, 3)), str(round(ys, 3)))
                abs_fe.append([e, str1])

            elif 'OOT' in abs_res[2]:
                if abs_res[2][-2] == 'x':
                    str2 = '%s: %s' % (str(abs_res[2][-2]), str(round(xs, 3)))
                elif abs_res[2][-2] == 'y':
                    str2 = '%s: %s' % (str(abs_res[2][-2]), str(round(ys, 3)))

                abs_fe.append([e, str2])

            if 'Both OOT' in rel_res[2]:
                str3 = 'x: %s, y: %s' % (str(round(xsr, 3)), str(round(ysr, 3)))
                rel_fe.append([e, str3])

            elif 'OOT' in rel_res[2]:
                if rel_res[2][-2] == 'x':
                    str4 = '%s: %s' % (str(rel_res[2][-2]), str(round(xsr, 3)))
                elif rel_res[2][-2] == 'y':
                    str4 = '%s: %s' % (str(rel_res[2][-2]), str(round(ysr, 3)))
                rel_fe.append([e, str4])

            # ## calculate the average FWHM from all four profiles
            mf = cdf.loc[cdf['energy'] == e, ['hor_fwhm', 'vert_fwhm', 'tlbr_fwhm', 'bltr_fwhm']].mean(axis =1).iloc[0]
            mf = round(mf, 3)
            efwhm = round(exp_fwhm[e],3)

            if mf > 1.1*efwhm or mf < 0.9*efwhm:
                r = '%s < e < %s' % (str(round(0.9*efwhm, 3)), str(round(1.1*efwhm,3)))
                mfwhm_fe= [p, e, r, mf]
                mfwhm.append(mfwhm_fe) # use mfwhm to covert to a table in the report

        # define whether the measurement pass or fail the absolute/ relative test.
        if not abs_fe:
            re_abs = 'Passed'
        else:
            re_abs = 'OOT'
            abs.append(abs_fe)

        if not rel_fe:
            re_rel = 'Passed'
        else:
            re_rel = 'OOT'
            rel.append(rel_fe)

        if not mfwhm_fe:
            re_mfwhm = 'Passed'
        else:
            re_mfwhm = 'OOT'


        line = [p,  re_abs,  re_rel, re_mfwhm]
        data.append(line)

        # find the x,y-shifts if they exceed the limit.

        if not abs_fe:
            if not rel_fe:
                remarks.update({p:{'abs': [], 'rel': []}})
            else:
                remarks.update({p:{'abs': [], 'rel': rel_fe}})

        else:
            if not rel_fe:
                remarks.update({p:{'abs': abs_fe, 'rel': []}})
            else:
                remarks.update({p:{'abs': abs_fe, 'rel': rel_fe}})

    abs_tab = []
    rel_tab = []
    for p in pos:
        if remarks[p]['abs']:
            for n, i  in enumerate(remarks[p]['abs']):
                if n == 0:
                    line = [p, i[0], i[1]]
                    abs_tab.append(line)
                    line = []
                else:
                    line = [[], i[0], i[1]]
                    abs_tab.append(line)
                    line = []

        if remarks[p]['rel']:
            for n, i  in enumerate(remarks[p]['rel']):
                if n == 0:
                    line = [p, i[0], i[1]]
                    rel_tab.append(line)
                    line = []
                else:
                    line = [[], i[0], i[1]]
                    rel_tab.append(line)
                    line = []

    return data, abs_tab, rel_tab, mspot, mfwhm

def make_shift_table(tab_list, pos):
    ''' tab_list is a nested list with all missing spots stored in a list [spot position, [list of energies ]]
        a table object from reportlab library will be resulted.

    '''
    obj = Table(tab_list)

    obj.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0,0), (-1, -1), 'CENTER'), \
                            ('BOX', (0, 0), (-1, -1), 2, colors.black), ('BOX', (0, 0), (0, -1), 2, colors.black), \
                            ('BOX', (0, 0), (-1, 0), 2, colors.black)]))

    # draw a line to separate each position
    for r in range(0, len(tab_list)):
        for c in range(0, len(tab_list[0])):
            if tab_list[r][c] in pos:
                obj.setStyle(TableStyle([('LINEABOVE', ( 0, r), (-1, r), 1, colors.black)]))

    return obj

def spot_report(df, p1, p2, fpath, gr_path, prof_path, comments, aEn):
    ''' aEn is the proton energy on the first gui'''
    # exam date
    date = pd.unique(df['date'])
    cdate = pd.to_datetime(date).astype(str).to_list()
    cdate = 'Date : ' + cdate[0]
    d = cdate.split()[2]

    # operators
    operators = 'Investigator(s) : %s %s' % (p1, p2 )

    # gantry angle
    gantry_angle = pd.unique(df['gantry_angle'])
    gantry_angle = 'Gantry angle = %s degree' % str(gantry_angle[0])
    ga = gantry_angle.split()[-2]

    # gantry
    gantry = pd.unique(df['gantry'])[0]
    gantry = 'Location : %s' % gantry
    g = gantry.split()[-1]

    # device
    device = pd.unique(df['device'])

    # spot position
    pos = pd.unique(df['spot'])

    data, abs_tab, rel_tab, mspot, mfwhm = make_table(df, aEn)
    # pos = list(remarks.keys())

    report_name = 'SG_G%s_GA%s_%s.pdf' % (g, ga, d)

    # document
    doc = SimpleDocTemplate(report_name,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)

    hp = ParagraphStyle('Normal')
    hp.textcolor = 'black'
    hp.fontsize = 10
    hp.fontName = 'Helvetica-Bold'
    hp.spaceAfter = 6
    hp.leading = 16
    hp.underlineWidth = 1


    bp = ParagraphStyle('Normal')
    bp.textcolor = 'black'
    bp.fontsize = 10
    bp.fontName = 'Helvetica'
    bp.spaceBefore = 3
    bp.spaceAfter = 3
    hp.leading = 12

    sp = ParagraphStyle('Normal')
    sp.textcolor = 'black'
    sp.fontsize = 15
    sp.fontName = 'Helvetica'
    sp.spaceBefore = 6
    sp.spaceAfter = 6
    sp.leading = 12


    story = []

    #  Report header
    report_title = ' %s spot grid analysis report' % device[0]
    story.append(Paragraph(report_title, hp))
    story.append(Paragraph(cdate, bp))
    story.append(Paragraph(gantry, bp))
    story.append(Paragraph(gantry_angle, bp))
    story.append(Paragraph(operators, bp))

    story.append(Spacer(1, 20))

    story.append(Paragraph('Result summary:', bp))


    t = Table(data)
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1, -1), 'MIDDLE'), ('ALIGN', (0,0), (-1, -1), 'CENTER'), \
                           ('BACKGROUND', (0, 0), (-1, -1), colors.lemonchiffon), ('BOX', (0, 0), (-1, -1), 2, colors.black), \
                           ('BOX', (0, 0), (0, -1), 2, colors.black), ('BOX', (0, 0), (-1, 0), 2, colors.black)]))

    for r in range(1, len(data)):
        for c in range(0, len(data[0])):
            if data[r][c] == 'OOT':
                t.setStyle(TableStyle([('BACKGROUND', (c, r), (c, r), colors.lightcoral)]))

    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph('** Result is defined as Out Of Tolerance (OOT) if one (or more than one) energy at the spot position exceeds the tolerance.' , sp))

    story.append(Spacer(1, 20))

    # comments
    story.append(Paragraph('Investigator comment(s):' , sp))
    if comments:
        story.append(Paragraph(str(comments), sp))
    else:
        story.append(Paragraph('NA' , sp))

    story.append(Spacer(1, 20))


    # absolute shift table
    if abs_tab:
        story.append(Paragraph('The spot positions and energies that fail the absolute tolerance:' , sp))


        at_h = ['Spot position', 'Energy (MeV)', 'Absolute shifts (mm)']
        abs_tab.insert(0, at_h)

        at = make_shift_table(abs_tab, pos)

        story.append(at)
        story.append(Spacer(1, 20))

    # relative shift table
    if rel_tab:
        story.append(Paragraph('The spot positions and energies that fail the relative tolerance:' , sp))

        rt_h = ['Spot position', 'Energy (MeV)', 'Relative shifts (mm)']
        rel_tab.insert(0, rt_h)

        rt = make_shift_table(rel_tab, pos)

        story.append(rt)
        story.append(Spacer(1, 20))

    # missing spot table
    if mspot:
        story.append(Paragraph('The script detects missing spot(s) as below:' , sp))

        ms_h = ['Spot position', 'Energy (MeV)']
        mspot.insert(0, ms_h)

        ms = make_shift_table(mspot, pos)

        story.append(ms)
        story.append(Spacer(1, 20))

    # mFWHM fails tolerance
    if mfwhm:
        story.append(Paragraph('The spot positions and energies that fail the FWHM tolerance:' , sp))

        mf_h = ['Spot position', 'Energy (MeV)', 'Expected FWHM (mm)', 'Measured FWHM (mm)']
        mfwhm.insert(0, mf_h)

        mft = make_shift_table(mfwhm, pos)
        story.append(mft)
        story.append(Spacer(1, 20))

    # ## put the images in the report
    images = [os.path.join(fpath, 'Absolute spot positions (2 mm tolerance).png'), \
              os.path.join(fpath, 'Absolute shifts (2 mm tolerance).png'), \
              os.path.join(fpath, 'Relative spot positions (1 mm tolerance).png'), \
              os.path.join(fpath, 'Relative shifts (1 mm tolerance).png')
               ]
              # os.path.join(fpath, 'fwhm_distribution.png'), \
              # os.path.join(fpath, 'gr_distribution.png')]
    image_mfwhm = os.path.join(fpath, 'mean_fwhm_per_spot_per_energy.png')
    image_fwhm = os.path.join(fpath, 'fwhm_distribution.png')
    image_gr = os.path.join(fpath, 'gr_distribution.png')



    for img in images:
        story.append(PageBreak())

        im = Image(img, width = 8.5*inch,  height = 8.5*inch,   hAlign = 'CENTER')
        story.append(im)

    # mean fwhm plot
    story.append(PageBreak())
    story.append(Paragraph('The averaged FWHM (i.e. spot size) is calculated from all four profiles per spot position per energy.' , sp))
    story.append(Image(image_mfwhm, width = 5*inch,  height = 4*inch,   hAlign = 'CENTER'))


    # fwhm plot
    story.append(PageBreak())
    story.append(Paragraph('The definition of four profiles per spot.' , sp))
    story.append(Image(prof_path, width = 2.5*inch,  height = 2.5*inch,   hAlign = 'CENTER' ))
    story.append(Spacer(1, 10))
    story.append(Paragraph('The scatterplots allow datapoints to have a small spread in x-axis such that we can better see the distribution.' , sp))
    story.append(Image(image_fwhm, width = 8*inch,  height = 5*inch,   hAlign = 'CENTER'))

    # gradient ratio plot
    story.append(PageBreak())
    story.append(Paragraph('The definition of the gradient ratio per profile.' , sp))
    story.append(Image(gr_path, width = 3*inch,  height = 2.5*inch,   hAlign = 'CENTER' ))
    story.append(Spacer(1, 10))
    story.append(Paragraph('The scatterplots allow the datapoints to have a small spread in x-axis such that we can better see the distribution. The mean value indicates as the grey dotted line and the median is the grey solid line.' , sp))
    story.append(Image(image_gr, width = 8*inch,  height = 5*inch,   hAlign = 'CENTER'))




    doc.build(story)



    return
