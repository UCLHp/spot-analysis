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

width, height = letter


# doc = SimpleDocTemplate("report.pdf",pagesize=letter)

# class to rotate the image
# when you rotate the image, you also rotate the origin of the image.
class RotatedImage(Image):
    def wrap(self,availWidth,availHeight):
         h, w = Image.wrap(self,availHeight,availWidth)
         return w, h
    def draw(self):
        self.canv.rotate(90)
        self.translate(width/5 *cm, height/5*cm)
        Image.draw(self )


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
            str = [p, e, 'Failed (y)']

    else:
        if ys < t and ys > -t:
            str = [p, e, 'Failed (x)']
        else:
            str = [p, e, 'Both Failed']

    return str

def make_table(df):

    ndf = df.groupby('spot')
    ndf = df.set_index('spot')

    t_rel = 1 # relative tolerance
    t_abs = 2 # absolute tolerance

    en = list(pd.unique(df['energy']))
    pos = list(pd.unique(df['spot']))

    data = []
    remarks = {}
    header = ['Positions', 'Absolute shifts within 2 mm', 'Relative shifts with 1 mm']
    data.append(header)


    rel = []
    abs = []

    mspot = [] # find the missing spot location and its energy
    for p in pos:
        cdf = ndf.loc[p]

        abs_fe = []
        rel_fe = []

        en_pos = list(pd.unique(cdf['energy']))

        # missing energy per spot location if any
        men = []
        if en_pos == en:
            pass
        else:
            # find the missing energy in that spot position
            for e in en:
                if e not in en_pos:
                    men.append(e)


        if men: # if men is not an empty list
            mspot.append([p, str(men[0])])


        for e in en_pos:
            #absolute shifts
            xs = cdf.loc[cdf['energy'] == e, 'x-shift-abs'].iloc[0]
            ys = cdf.loc[cdf['energy'] == e, 'y-shift-abs'].iloc[0]

            # relative shifts
            xsr = cdf.loc[cdf['energy'] == e, 'x-shift-rel'].iloc[0]
            ysr = cdf.loc[cdf['energy'] == e, 'y-shift-rel'].iloc[0]

            abs_res = pass_fail(xs, ys, t_abs, e, p)
            rel_res = pass_fail(xsr, ysr, t_rel, e, p)

            # find the fail (x,y)
            if 'Both Failed' in abs_res[2]:
                str1 = 'x: %s, y: %s ' % (str(round(xs, 3)), str(round(ys, 3)))
                abs_fe.append([e, str1])

            elif 'Failed' in abs_res[2]:
                if abs_res[2][-2] == 'x':
                    str2 = '%s: %s' % (str(abs_res[2][-2]), str(round(xs, 3)))
                elif abs_res[2][-2] == 'y':
                    str2 = '%s: %s' % (str(abs_res[2][-2]), str(round(ys, 3)))

                abs_fe.append([e, str2])

            if 'Both Failed' in rel_res[2]:
                str3 = 'x: %s, y: %s' % (str(round(xsr, 3)), str(round(ysr, 3)))
                rel_fe.append([e, str3])

            elif 'Failed' in rel_res[2]:
                if rel_res[2][-2] == 'x':
                    str4 = '%s: %s' % (str(rel_res[2][-2]), str(round(xsr, 3)))
                elif rel_res[2][-2] == 'y':
                    str4 = '%s: %s' % (str(rel_res[2][-2]), str(round(ysr, 3)))
                rel_fe.append([e, str4])


        # define whether the measurement pass or fail the absolute/ relative test.
        if not abs_fe:
            re_abs = 'All Passed'
        else:
            re_abs = 'Failed'
            abs.append(abs_fe)

        if not rel_fe:
            re_rel = 'All Passed'
        else:
            re_rel = 'Failed'
            rel.append(rel_fe)


        line = [p,  re_abs,  re_rel]
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


    # # print(f'data: {data}')
    # print(f'abs: {abs_tab} \n rel: {rel_tab}')
    #
    # print(f'mspot : {mspot}')

    return data, abs_tab, rel_tab, mspot

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

def spot_report(df, p1, p2, fpath, gr_path, prof_path):
    # exam date
    date = pd.unique(df['date'])
    cdate = pd.to_datetime(date).astype(str).to_list()
    cdate = 'Date : ' + cdate[0]

    # operators
    operators = 'Investigator(s) : %s %s' % (p1, p2 )

    # gantry angle
    gantry_angle = pd.unique(df['gantry_angle'])
    gantry_angle = 'Gantry angle = %s degree' % str(gantry_angle[0])

    # gantry
    gantry = pd.unique(df['gantry'])[0]
    gantry = 'Location : %s' % gantry

    # device
    device = pd.unique(df['device'])

    # spot position
    pos = pd.unique(df['spot'])

    data, abs_tab, rel_tab, mspot = make_table(df)
    # pos = list(remarks.keys())

    # document
    doc = SimpleDocTemplate("report.pdf",pagesize=letter,
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
            if data[r][c] == 'Failed':
                t.setStyle(TableStyle([('BACKGROUND', (c, r), (c, r), colors.lightcoral)]))

    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph('** Result is defined as failed if one (or more than one) energy at the spot position exceeds the limit.' , sp))

    story.append(Spacer(1, 50))

    # absolute shift table
    if abs_tab:
        # print(f'abs_tab: {abs_tab}')
        story.append(Paragraph('The spot positions and energies that fail the absolute limit:' , sp))


        at_h = ['Spot position', 'Energy (MeV)', 'Absolute shits (mm)']
        abs_tab.insert(0, at_h)

        at = make_shift_table(abs_tab, pos)
        # at = Table(abs_tab)
        #
        # at.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0,0), (-1, -1), 'CENTER'), \
        #                         ('BOX', (0, 0), (-1, -1), 2, colors.black), ('BOX', (0, 0), (0, -1), 2, colors.black), \
        #                         ('BOX', (0, 0), (-1, 0), 2, colors.black)]))
        #
        # # draw a line to separate each position
        # for r in range(0, len(abs_tab)):
        #     for c in range(0, len(abs_tab[0])):
        #         if abs_tab[r][c] in pos:
        #             at.setStyle(TableStyle([('LINEABOVE', ( 0, r), (-1, r), 1, colors.black)]))

        story.append(at)
        story.append(Spacer(1, 20))

    # relative shift table
    if rel_tab:
        story.append(Paragraph('The spot positions and energies that fail the relative limit:' , sp))

        rt_h = ['Spot position', 'Energy (MeV)', 'Relative shits (mm)']
        rel_tab.insert(0, rt_h)

        rt = make_shift_table(rel_tab, pos)

        # rt = Table(rel_tab)
        #
        # rt.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0,0), (-1, -1), 'CENTER'), \
        #                         ('BOX', (0, 0), (-1, -1), 2, colors.black), ('BOX', (0, 0), (0, -1), 2, colors.black), \
        #                         ('BOX', (0, 0), (-1, 0), 2, colors.black)]))
        #
        # # draw a line to separate each position
        # for r in range(0, len(rel_tab)):
        #     for c in range(0, len(rel_tab[0])):
        #         if rel_tab[r][c] in pos:
        #             rt.setStyle(TableStyle([('LINEABOVE', ( 0, r), (-1, r), 1, colors.black)]))

        story.append(rt)
        story.append(Spacer(1, 20))

    # missing spot table
    if mspot:
        story.append(Paragraph('The script detects missing spot as below:' , sp))

        ms_h = ['Spot position', 'Energy (MeV)']
        mspot.insert(0, ms_h)



        ms = make_shift_table(mspot, pos)


        story.append(ms)
        story.append(Spacer(1, 20))



    # ## put the images in the report
    images = [os.path.join(fpath, 'spot_grid (tolerance = 2 mm).png'), \
              os.path.join(fpath, 'x-y-shifts_tol_2mm.png'), \
              os.path.join(fpath, 'spot_grid (tolerance = 1 mm).png'), \
              os.path.join(fpath, 'x-y-shifts_tol_1mm.png')
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
    story.append(Paragraph('The averaged fwhm is calculated from all four profiles per spot position per energy.' , sp))
    story.append(Image(image_mfwhm, width = 5*inch,  height = 4*inch,   hAlign = 'CENTER'))


    # fwhm plot
    story.append(PageBreak())
    story.append(Paragraph('The definition of four profiles per spot.' , sp))
    # i = Image(image_fwhm, width = 8*inch,  height = 6*inch,   hAlign = 'CENTER')
    # story.append(RotatedImage(image_fwhm, width/2 , height/2,   hAlign = 'RIGHT'))
    story.append(Image(prof_path, width = 2.5*inch,  height = 2.5*inch,   hAlign = 'CENTER' ))
    story.append(Spacer(1, 10))
    story.append(Paragraph('The scatterplots allow datapoints to have a small spread in x-axis such that we can better see the distribution.' , sp))
    story.append(Image(image_fwhm, width = 8*inch,  height = 5*inch,   hAlign = 'CENTER'))

    # gradient ratio plot
    story.append(PageBreak())
    story.append(Paragraph('The definition of the gradient ratio per profile.' , sp))
    story.append(Image(gr_path, width = 3*inch,  height = 2.5*inch,   hAlign = 'CENTER' ))
    story.append(Spacer(1, 10))
    story.append(Paragraph('The scatterplots allow the datapoints to have a small spread in x-axis such that we can better see the distribution.' , sp))
    story.append(Image(image_gr, width = 8*inch,  height = 5*inch,   hAlign = 'CENTER'))
    # i = Image(image_gr, width = 8*inch,  height = 6*inch,   hAlign = 'CENTER')
    # story.append(RotatedImage(image_gr, 0.5*width , 0.5*height,  hAlign = 'LEFT')) #(self, image, x,y, width=None,height=None)





    doc.build(story)



    return