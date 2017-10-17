#!python3
'''Module for making the PDF versions of the Single Student View tab
   from the main report'''

import warnings
from datetime import date
from collections import OrderedDict
from fpdf import FPDF

def compute_excel(string, data_row):
    '''Takes a string encoded as an excel formula and returns a numeric
    (float) response. Data from the student roster table is provided
    in order to be replaced by Excel references'''
    return None

def clean_excel(string, data_row):
    '''Takes a string encoded as an Excel formula and returns a plain
    text string for pdf printing. Data from the student roster table
    is provided in data_row and could be replace based on the an Excel
    reference'''
    # We need to do these in order so that the quotes at the end aren't
    # replaced inside the formulas in the beginning
    translation = OrderedDict([
            ['TEXT(TODAY(),"mm/dd")', date.today().strftime('%m/%d')],
            ['TEXT(TODAY(),"m/d")', date.today().strftime('%m/%d')],
            ['INDEX(Counselor,MATCH(D3,KidIDs,0))','tbl:Counselor'],
            ['INDEX(Advisors,MATCH(D3,KidIDs,0))','tbl:Advisor'],
            ['INDEX(Cohort,MATCH(D3,KidIDs,0))','tbl:Cohort'],
            ['&',''],
            ['=',''],
            ['"',''],
            ])
    for old, new in translation.items():
        if old in string:
            if new.startswith('tbl:'):
                string = string.replace(old, data_row[new[4:]])
            else:
                string = string.replace(old, new)
    return string

def shrink_cell(pdf, w, txt, h, border, ln, align, fill):
    ''' writes a cell, but cuts off last characters if too long'''
    while w < pdf.get_string_width(txt):
        txt = txt[:-1]
    pdf.cell(w=w, txt=txt, h=h, border=border,
            ln=ln, align=align, fill=fill)

def make_pdf_report(fn, dfs, cfg, cfg_ssv, campus, debug):
    '''Master function for creating the pdf reports'''

    # First create Class and process config settings
    local_cfg = {}
    for label, ssv_name in [('orient', 'pdf_orientation'),
                            ('c_header', 'counselor_header'),
                            ('p_header', 'print_header'),
                            ('p_footer', 'print_footer'),
                            ]:
        if campus in cfg_ssv[ssv_name]:
            local_cfg[label] = cfg_ssv[ssv_name][campus]
        else:
            local_cfg[label] = cfg_ssv[ssv_name]['Standard']

    top_margin = cfg_ssv['pdf_margins']['top']
    left_margin = cfg_ssv['pdf_margins']['left']
    right_margin = cfg_ssv['pdf_margins']['right']
    thick_line = cfg_ssv['pdf_lines']['thick']
    line = cfg_ssv['pdf_lines']['line']

    pdf = FPDF(orientation = local_cfg['orient'],
            unit = 'in', format = 'Letter')

    for font_name, filename in cfg_ssv['pdf_fonts'].items():
        pdf.add_font(font_name, '', filename, uni=True)
    pdf.set_line_width(line)
    pdf.set_margins(left=left_margin, top=top_margin, right=right_margin)

    # Get the student data and sort as appropriate
    df = dfs['roster'].copy()
    if debug:
        print(df.index)
        print(df.columns)
    ##NEED A SORT HERE

    # start repeating here
    for i, stu_data in df.iterrows():
        pdf.add_page()

        pdf.set_y(top_margin)

        w = cfg_ssv['pdf_widths'] # list of cell widths in inches
        h = cfg_ssv['pdf_heights'] # list of cell heights in inches

        # The width of next two columns is variable based on header sizes
        # First row
        name_text = ('College application odds report for '+
                stu_data['First']+' '+stu_data['Last'])
        c_text = clean_excel(local_cfg['c_header'],stu_data)
        pdf.set_font('font_b', '', 11)
        c_width = pdf.get_string_width(c_text)+0.05

        if local_cfg['p_header']:
            # We're squeezing in one more entry, so stealing off the name
            # and the counselor header
            pdf.set_font('font_i', '', 11)
            p_text = clean_excel(local_cfg['p_header'], stu_data)
            p_width = pdf.get_string_width(p_text)+0.05
            n_width = sum(w) - p_width - c_width - 0.05
        else:
            n_width = sum(w) - c_width - 0.05

        pdf.set_font('font_b', '', 14)
        shrink_cell(pdf=pdf, w=n_width, txt=name_text,
                h=h[0], border = 0, ln = 0, align = 'L', fill = False)

        if local_cfg['p_header']:
            pdf.set_font('font_i', '', 11)
            shrink_cell(pdf=pdf, w=p_width, txt=p_text,
                    h=h[0], border = 0, ln = 0, align = 'L', fill = False)

        pdf.set_font('font_b', '', 11)
        shrink_cell(pdf=pdf, w=c_width, txt=c_text,
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

        # Skinny lines
        pdf.set_line_width(line)

    # The font we use is missing an unusued glyph and so throws two warnings
    # at save. The next two lines supress this, but probably good to
    # occasionally uncomment them
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pdf.output(fn, 'F')