#!python3

import warnings
from fpdf import FPDF

def make_pdf_report(fn, dfs, cfg, cfg_ssv, campus, debug):
    '''Master function for creating the pdf reports'''

    # First create Class and process config settings
    if campus in cfg_ssv['pdf_orientation']:
        orient = cfg_ssv['pdf_orientation'][campus]
    else:
        orient = cfg_ssv['pdf_orientation']['Standard']

    top_margin = cfg_ssv['pdf_margins']['top']
    left_margin = cfg_ssv['pdf_margins']['left']
    right_margin = cfg_ssv['pdf_margins']['right']
    thick_line = cfg_ssv['pdf_lines']['thick']
    line = cfg_ssv['pdf_lines']['line']

    pdf = FPDF(orientation = orient, unit = 'in', format = 'Letter')

    for font_name, filename in cfg_ssv['pdf_fonts'].items():
        pdf.add_font(font_name, '', filename, uni=True)
    pdf.set_line_width(line)
    pdf.set_margins(left=left_margin, top=top_margin, right=right_margin)

    pdf.add_page()

    pdf.set_font('font_b', '', 14)
    pdf.set_y(top_margin)

    w = cfg_ssv['pdf_widths'] # list of cell widths in inches
    h = cfg_ssv['pdf_heights'] # list of cell heights in inches

    # The width of next two rows is variable if special header
    # First row
    pdf.cell(w=sum(w[:3]),
            txt='College application odds report for Example Student',
            h=h[0], border = 0, ln = 0, align = 'L', fill = False)

    pdf.cell(w=w[3], txt='',
            h=h[0], border = 0, ln = 0, align = 'L', fill = False)

    pdf.set_font('font_b', '', 11)
    pdf.cell(w=sum(w[4:]), txt='Cnslr: Ballard (B1)',
            h=h[0], border = 0, ln = 1, align = 'L', fill = False)

    # Second row
    pdf.set_fill_color(r=220,g=230,b=241)
    pdf.cell(w=w[0], txt="Student's name:",
            h=h[1], border = 1, ln = 0, align = 'L', fill = True)

    pdf.set_font('font_r', '', 11)
    pdf.cell(w=w[1], txt='ACT/SAT',
            h=h[1], border = 'B', ln = 0, align = 'C', fill = True)

    pdf.cell(w=w[2], txt='GPA',
            h=h[1], border = 'B', ln = 0, align = 'C', fill = True)

    pdf.cell(w=w[3], txt='Race/Eth',
            h=h[1], border = 1, ln = 0, align = 'C', fill = True)

    pdf.cell(w=w[4], txt='IGR', # check for special names
            h=h[1], border = 'B', ln = 0, align = 'C', fill = True)

    pdf.cell(w=w[5], txt='74%',
            h=h[1], border = 'B', ln = 1, align = 'C', fill = False)

    # Third row
    pdf.set_fill_color(r=253,g=233,b=217)
    pdf.cell(w=w[0], txt='Last, First',
            h=h[2], border = 1, ln = 0, align = 'L', fill = True)

    pdf.cell(w=w[1], txt='22/1120',
            h=h[2], border = 0, ln = 0, align = 'C', fill = False)

    pdf.cell(w=w[2], txt='3.57',
            h=h[2], border = 0, ln = 0, align = 'C', fill = False)

    pdf.cell(w=w[3], txt='H',
            h=h[2], border = 1, ln = 0, align = 'C', fill = False)

    pdf.set_fill_color(r=220,g=230,b=241)
    pdf.cell(w=w[4], txt='TGR', # check for special names
            h=h[2], border = 'T', ln = 0, align = 'C', fill = True)

    pdf.cell(w=w[5], txt='68%',
            h=h[2], border = 0, ln = 1, align = 'C', fill = False)

    # Fourth row

    # Bold lines
    pdf.set_line_width(thick_line)
    pdf.rect(left_margin, top_margin+h[0], # around name
            w[0], sum(h[1:3]))

    pdf.rect(left_margin, top_margin+h[0], # around name and scores/gpa
            sum(w[:3]), sum(h[1:3]))

    pdf.rect(left_margin, top_margin+h[0], # around whole left side
            sum(w[:3]), sum(h[1:6]))

    pdf.rect(left_margin+sum(w[:4]), top_margin+h[0], # upper right
            sum(w[4:]), sum(h[1:3]))

    pdf.rect(left_margin+sum(w[:3]), top_margin+sum(h[:3]), # lower right
            sum(w[3:]), sum(h[3:6]))

    pdf.line(left_margin,top_margin,left_margin+sum(w[:4]),top_margin)
    pdf.set_line_width(line)

    # The font we use is missing an unusued glyph and so throws two warnings
    # at save. The next two lines supress this, but probably good to
    # occasionally uncomment them
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pdf.output(fn, 'F')
