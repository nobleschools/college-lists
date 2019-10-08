#!python3
'''Module for making the PDF versions of the Single Student View tab
   from the main report'''

import warnings
import numpy as np
from datetime import date
from collections import OrderedDict
from fpdf import FPDF

def _notnan(value, nanstring, formatstring):
    '''Returns a string from a numeric value formatting by formatstring
    if not nan; otherwise returns the nanstring'''
    if isinstance(value, str):
        return value
    try:
        if np.isnan(value):
            return nanstring
        else:
            return formatstring.format(value)
    except:
        print('Failed value: {}'.format(value))
        raise

def _clean_excel(string, data_row, labels):
    """
    Takes a string encoded as an Excel formula and returns a plain
    text string for pdf printing. Data from the student roster table
    is provided in data_row and could be replace based on the an Excel
    reference
    """
    # We need to do these in order so that the quotes at the end aren't
    # replaced inside the formulas in the beginning
    translation = OrderedDict([
            ['TEXT(TODAY(),"mm/dd")', date.today().strftime('%m/%d')],
            ['TEXT(TODAY(),"m/d")', date.today().strftime('%m/%d')],
            ['INDEX(Strats,MATCH(D3,KidIDs,0))','tbl:local_strategy'],
            ['INDEX(EFC,MATCH(D3,KidIDs,0))','tbl:EFC'],
            ['INDEX(Counselor,MATCH(D3,KidIDs,0))','tbl:Counselor'],
            ['INDEX(Advisors,MATCH(D3,KidIDs,0))','tbl:Advisor'],
            ['INDEX(Cohort,MATCH(D3,KidIDs,0))','tbl:Cohort'],
            ['INDEX(Campus,MATCH(D3,KidIDs,0))','tbl:Campus'],
            ['LOWER(TargetGRLabel)',labels['TargetGR'].lower()],
            ['LOWER(IdealGRLabel)',labels['IdealGR'].lower()],
            ['LOWER(FarBelowTGRLabel)',labels['FarBelowTGR'].lower()],
            ['LOWER(MatchLabel)',labels['Match'].lower()],
            ['LOWER(ReachLabel)',labels['Reach'].lower()],
            ['LOWER(SafetyLabel)',labels['Safety'].lower()],
            ['LOWER(LongshotLabel)',labels['Longshot'].lower()],
            ['LOWER(HailMaryLabel)',labels['HailMary'].lower()],
            ['&',''],
            ['=',''],
            ['"',''],
            ])
    for old, new in translation.items():
        if old in string:
            if new.startswith('tbl:'):
                string = string.replace(old, _notnan(
                    data_row[new[4:]],'N/A','{}'))
            else:
                string = string.replace(old, new)
    return string

def _shrink_cell(pdf, w, txt, h, border, ln, align, fill):
    ''' writes a cell, but cuts off last characters if too long'''
    while w < pdf.get_string_width(txt):
        txt = txt[:-1]
    pdf.cell(w=w, txt=txt, h=h, border=border,
            ln=ln, align=align, fill=fill)


def _set_color_name(pdf, name, type='fill'):
    """Helper function to encapsulate RGB codes"""
    colors = { 'light_blue': (220,230,241),
               'salmon':     (253,233,217),
               'grey':       (217,217,217),
               'navy_blue':  (0,  32, 96),
               'red':        (255,0,  0),
               'black':      (0,  0,  0),
             }
    if name in colors:
        r,g,b=colors[name]
        if type == 'fill':
            pdf.set_fill_color(r=r,g=g,b=b)
        elif type == 'text':
            pdf.set_text_color(r=r,g=g,b=b)
    else:
        raise(RuntimeError('PDF color not specified: '+name))


def make_pdf_report(fn, dfs, cfg, cfg_ssv, campus, debug):
    '''Master function for creating the pdf reports'''

    # First create Class and process config settings
    local_cfg = {}
    for label, cfg_name in [('sort', 'sort_students'),
                            ('labels', 'category_labels'),
                            ]:
        if campus in cfg[cfg_name]:
            local_cfg[label] = cfg[cfg_name][campus]
        else:
            local_cfg[label] = cfg[cfg_name]['Standard']

    labels = local_cfg['labels']
    tgr_label = labels['TargetGR']
    igr_label = labels['IdealGR']
    

    for label, ssv_name in [('orient', 'pdf_orientation'),
                            ('c_header', 'counselor_header'),
                            ('p_header', 'print_header'),
                            ('p_footer', 'print_footer'),
                            ]:
        if campus in cfg_ssv[ssv_name]:
            local_cfg[label] = cfg_ssv[ssv_name][campus]
        else:
            local_cfg[label] = cfg_ssv[ssv_name]['Standard']

    if campus in cfg_ssv['school_goals']:
        school_goals = cfg_ssv['school_goals'][campus]
        goal_descriptions = cfg_ssv['goal_descriptions']
    else:
        school_goals = None

    top_margin = cfg_ssv['pdf_margins']['top']
    left_margin = cfg_ssv['pdf_margins']['left']
    right_margin = cfg_ssv['pdf_margins']['right']
    thick_line = cfg_ssv['pdf_lines']['thick']
    line = cfg_ssv['pdf_lines']['line']
    goals_start = cfg_ssv['pdf_goals_start']
    footer_start = cfg_ssv['pdf_footer_start']
    college_max = cfg_ssv['pdf_college_max']

    pdf = FPDF(orientation = local_cfg['orient'],
            unit = 'in', format = 'Letter')

    for font_name, filename in cfg_ssv['pdf_fonts'].items():
        pdf.add_font(font_name, '', filename, uni=True)
    pdf.set_line_width(line)
    pdf.set_margins(left=left_margin, top=top_margin, right=right_margin)

    # Get the student data and sort as appropriate
    df = dfs['roster'].copy()
    app_df = dfs['apps'].copy()

    # The sort string is pseudocode linking table columns surrounded by % with
    # ampersands and preceded by an equals to map to an Excel formula. The
    # next line reduces that to an ordered list of table names
    sort_order = [x for x
            in local_cfg['sort'].split(sep='%') if x not in ['=','&','']]
    if debug:
        print('Sort order for PDF: {}'.format(str(sort_order)))
    df.sort_values(by=sort_order, inplace=True)

    ####################################
    # start repeating here for each page
    for i, stu_data in df.iterrows():
        pdf.add_page()

        pdf.set_y(top_margin)

        w = cfg_ssv['pdf_widths'] # list of cell widths in inches
        h = cfg_ssv['pdf_heights'] # list of cell heights in inches

        # The width of next two columns is variable based on header sizes
        # *First row
        name_text = ('College application odds report for '+
                stu_data['First']+' '+stu_data['Last'])
        c_text = _clean_excel(local_cfg['c_header'],stu_data,labels)
        pdf.set_font('font_b', '', 11)
        c_width = pdf.get_string_width(c_text)+0.05

        if local_cfg['p_header']:
            # We're squeezing in one more entry, so stealing off the name
            # and the counselor header
            pdf.set_font('font_i', '', 11)
            p_text = _clean_excel(local_cfg['p_header'], stu_data, labels)
            p_width = pdf.get_string_width(p_text)+0.05
            n_width = sum(w) - p_width - c_width - 0.05
        else:
            n_width = sum(w) - c_width - 0.05

        pdf.set_font('font_b', '', 14)
        _shrink_cell(pdf=pdf, w=n_width, txt=name_text,
                h=h[0], border = 0, ln = 0, align = 'L', fill = False)

        if local_cfg['p_header']:
            pdf.set_font('font_i', '', 11)
            _shrink_cell(pdf=pdf, w=p_width, txt=p_text,
                    h=h[0], border = 0, ln = 0, align = 'L', fill = False)

        pdf.set_font('font_b', '', 11)
        _shrink_cell(pdf=pdf, w=c_width, txt=c_text,
                h=h[0], border = 0, ln = 1, align = 'L', fill = False)

        # *Second row
        _set_color_name(pdf, 'light_blue')
        pdf.cell(w=w[0], txt="Student's name:",
                h=h[1], border = 1, ln = 0, align = 'L', fill = True)

        pdf.set_font('font_r', '', 11)
        pdf.cell(w=w[1], txt='ACT/SAT',
                h=h[1], border = 'B', ln = 0, align = 'C', fill = True)

        pdf.cell(w=w[2], txt='GPA',
                h=h[1], border = 'B', ln = 0, align = 'C', fill = True)

        pdf.cell(w=w[3], txt='Race/Eth',
                h=h[1], border = 1, ln = 0, align = 'C', fill = True)

        txt = igr_label[0]+'GR'
        pdf.cell(w=w[4], txt=txt,
                h=h[1], border = 'B', ln = 0, align = 'C', fill = True)

        txt = _notnan(stu_data['local_ideal_gr'],'TBD','{:2.0%}')
        pdf.cell(w=w[5], txt=txt,
                h=h[1], border = 'B', ln = 1, align = 'C', fill = False)

        # *Third row
        _set_color_name(pdf, 'salmon')
        pdf.cell(w=w[0], txt=stu_data['LastFirst'],
                h=h[2], border = 1, ln = 0, align = 'L', fill = True)

        txt = (_notnan(stu_data['ACT'],'TBD','{:d}')+'/'+
               _notnan(stu_data['SAT'],'TBD','{:d}')) 
        pdf.cell(w=w[1], txt=txt,
                h=h[2], border = 0, ln = 0, align = 'C', fill = False)

        pdf.cell(w=w[2], txt=_notnan(stu_data['GPA'],'TBD','{:4.2f}'),
                h=h[2], border = 0, ln = 0, align = 'C', fill = False)

        pdf.cell(w=w[3], txt=_notnan(stu_data['Race/ Eth'],'TBD','{}'),
                h=h[2], border = 1, ln = 0, align = 'C', fill = False)

        _set_color_name(pdf, 'light_blue')
        txt = tgr_label[0]+'GR'
        pdf.cell(w=w[4], txt=txt,
                h=h[2], border = 'T', ln = 0, align = 'C', fill = True)

        txt = _notnan(stu_data['local_target_gr'],'TBD','{:2.0%}')
        pdf.cell(w=w[5], txt=txt,
                h=h[2], border = 0, ln = 1, align = 'C', fill = False)

        # *Fourth row
        pdf.set_font('font_b', '', 11)
        pdf.cell(w=w[0], txt='Odds of 1 or more acceptances to:',
                h=h[3], border = 0, ln = 0, align = 'L', fill = True)

        txt = _notnan(stu_data['local_sat_max'],'TBD','{:1.0f}')
        pdf.cell(w=w[1], txt=txt, h=h[3], border=0, ln=0, align='C', fill=True)

        pdf.cell(w=w[2], txt='', h=h[3], border=0, ln=0, align='C', fill=True)

        pdf.cell(w=sum(w[3:]), txt='Goals for #s to the left:',
                h=h[3], border=0, ln=1, align='L', fill=True)

        # *Fifth row
        pdf.set_font('font_r', '', 11)
        pdf.cell(w=sum(w[:2]),
            txt='"Money" '+tgr_label+' grade rate ('+tgr_label[0]+
            'GR) or better schools',
            h=h[4], border=0, ln=0, align='L', fill=False)

        txt = _notnan(stu_data['local_oneplus_mtgr'], 'TBD','{:3.0%}')
        pdf.cell(w=w[2], txt=txt,
                h=h[4], border = 0, ln = 0, align = 'C', fill = False)

        txt='<--Shoot for at least 90% for Money '+tgr_label[0]+'GR'
        pdf.cell(w=sum(w[3:]), txt=txt, h=h[4], border=0, ln=1,
                align='L', fill=False)

        # *Sixth row
        pdf.cell(w=sum(w[:2]),
            txt='"Money" '+igr_label+' grade rate ('+igr_label[0]+
            'GR) or better schools',
            h=h[5], border=0, ln=0, align='L', fill=False)

        txt = _notnan(stu_data['local_oneplus_migr'], 'TBD','{:3.0%}')
        pdf.cell(w=w[2], txt=txt,
                h=h[5], border = 0, ln = 0, align = 'C', fill = False)

        txt='<--Shoot for at least 50% for Money '+igr_label[0]+'GR'
        pdf.cell(w=sum(w[3:]), txt=txt, h=h[5], border=0, ln=1,
                align='L', fill=False)

        # *Seventh row is skinny/skip row
        pdf.cell(w=w[0], txt='', h=h[6], border=0, ln=1, align='C', fill=False)

        # *Eighth row is header for college lists and is actually the first of
        # *two rows used for that purpose
        pdf.set_font('font_b', '', 11)
        pdf.cell(w=w[0],
            txt='Schools currently applying to ("*" indicates',
            h=h[7], border=0, ln=0, align='L', fill=True)

        if ((stu_data['Race/ Eth'] == 'W') or
            (stu_data['Race/ Eth'] == 'A')):
            txt_race = '6 yr (all)'
        else:
            txt_race = '6 yr AA/H'

        for w_this, txt_this, ln_this in [
                (w[1], txt_race, 0),
                (w[2], 'Odds of', 0),
                (w[3], 'For you,', 0),
                (w[4], '', 0),
                (w[5], '', 1)
                # (0.8,'Award',0), # Replace the above with these two for new "award" column
                # (0.9,'Award letter',1)
                ]:
            pdf.cell(w=w_this, h=h[7], txt=txt_this, ln=ln_this,
                border=0, align='C', fill=True)

        # *Ninth row is continuation of college header
        pdf.cell(w=w[0], txt='prospective):',
            h=h[8], border=0, ln=0, align='L', fill=True)

        for w_this, txt_this, ln_this in [
                (w[1], 'Grad Rate', 0),
                (w[2], 'Admit', 0),
                (w[3], 'school is a', 0),
                (w[4], 'App Status', 0),
                (w[5], 'Award code', 1)
                # (0.80, 'code', 0), # Replace the above with these two for new "award" column
                # (0.9, 'received', 1)
                ]:
            pdf.cell(w=w_this, h=h[8], txt=txt_this, ln=ln_this,
                border=0, align='C', fill=True)

        # From here on, we'll have a variable # of rows
        stu_apps = app_df[app_df['hs_student_id'] == i]
        num_apps = len(stu_apps)
        pdf.set_font('font_r', '', 11)
        tgr = stu_data['local_target_gr']
        igr = stu_data['local_ideal_gr']
        _set_color_name(pdf, 'light_blue')
        apps_displayed=0
        if num_apps:
            for j, app_data in stu_apps.iterrows():
                college_text = app_data['collegename']
                _shrink_cell(pdf=pdf, w=w[0], h=h[9], ln=0, txt=college_text,
                        align='L', fill=False, border=0)

                # This block is complicated because of grad rate highlighting
                gr_this = app_data['local_6yr_all_aah']
                gr_text = _notnan(gr_this,'N/A','{:2.0%}')
                if gr_this >= igr:
                    _set_color_name(pdf, 'navy_blue', type='text')
                    pdf.set_font('font_b', '', 11)
                if gr_this < tgr:
                    _set_color_name(pdf, 'red', type='text')
                    _set_color_name(pdf, 'grey')
                gr_fill = gr_this < tgr
                pdf.cell(w=w[1], h=h[9], ln=0, txt=gr_text,
                        align='C', fill=gr_fill, border=0)

                # Back to normal for last entries
                _set_color_name(pdf, 'black', type='text')
                pdf.set_font('font_r', '', 11)

                for w_, txt_, ln_ in [
                     (w[2], _notnan(app_data['local_odds']/100.0,
                                   'N/A','{:2.0%}'), 0),
                     (w[3], app_data['local_class'], 0),
                     (w[4], app_data['local_result'], 0),
                     (w[5], _notnan(app_data['local_money_code'],#(0.8, _notnan(app_data['local_money_code'],
                                                            'N/A','{}'), 1)
                ]:
                    pdf.cell(w=w_, h=h[9], txt=txt_, align='C', fill=False,
                            ln=ln_, border=0)
                apps_displayed += 1
                if apps_displayed == college_max:
                    break

        # Optional school based goals at the bottom
        if school_goals is not None:
            pads, goal_eval = _get_student_goal_performance(pdf, w[0],
                               school_goals, goal_descriptions, stu_data,
                               stu_apps, labels)

            pdf.set_y(goals_start)
            # Two header lines:
            pdf.set_font('font_bi', '', 11)           
            pdf.cell(w=w[0], h=h[10], border=0, ln=1, align='L', fill=False,
                txt='Your list compared to campus goals:')
            
            pdf.set_font('font_b', '', 11)
            _set_color_name(pdf, 'light_blue')

            if pads > 0:
                padder = max([1,pads-3])*' '
            else:
                padder = ''
            pdf.cell(w=w[0], h=h[10], border=0, ln=0, align='L', fill=True,
                txt=(padder+'Campus Goal'))
            pdf.cell(w=w[1], h=h[10], border=0, ln=0, align='C', fill=True,
                txt='You')
            pdf.cell(w=w[1], h=h[10], border=0, ln=1, align='C', fill=True,
                txt='Met?')
                
            # Now do the variable number of goals
            pdf.set_font('font_r', '', 11)
            for goal_text, score, judgement in goal_eval:
                pdf.cell(w=w[0], h=h[10], border=0, ln=0, align='L', fill=False,
                    txt=(pads*' '+goal_text))
                pdf.cell(w=w[1], h=h[10], border=0, ln=0, align='C', fill=False,
                    txt=score)
                pdf.cell(w=w[1], h=h[10], border=0, ln=1, align='C', fill=False,
                    txt=judgement)

        # Final (optional) print line for a page
        if local_cfg['p_footer']:
            pdf.set_y(footer_start)
            pdf.set_font('font_bi', '', 11)
            p_text = _clean_excel(local_cfg['p_footer'], stu_data, labels)
            pdf.cell(w=sum(w), h=h[11], border='T', ln=0, align='L', fill=False,
                txt=p_text)
            
        # Final formatting of lines: bold rects then lines
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
                
        if school_goals is not None:
            pdf.rect(left_margin, goals_start+h[10],
                    sum([w[0],w[1],w[1]]), h[10]*(1+len(school_goals)))

        # Skinny rects then lines
        pdf.set_line_width(line)
        line_top = top_margin+sum(h[:7])
        line_bottom = top_margin+sum(h[:9])+h[9]*(
                        num_apps if num_apps <= college_max else college_max)
        for x in [1, 2, 4, 5]:
            pdf.line(left_margin+sum(w[:x]),line_top,
                     left_margin+sum(w[:x]),line_bottom)
        #pdf.line(left_margin+sum(w[:x])+0.8,line_top,
        #         left_margin+sum(w[:x])+0.8,line_bottom)

    # The font we use is missing an unusued glyph and so throws two warnings
    # at save. The next three lines supress this, but probably good to
    # occasionally uncomment them
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pdf.output(fn, 'F')

def _get_student_goal_performance(pdf, w, school_goals, goal_descriptions,
                                     stu_data, stu_apps, labels):
    """
    Utility function to return a list of lists with entries for the bottom
    Campus goals box. w is the width in inches of the main cell so that
    "pads" can return the number of spaces to front pad the set.
    """
    goal_eval = []
    for i in range(len(school_goals)):
        label, amount = list(school_goals[i].items())[0]
                
        # Goals are usually integers, but there can be extra logic
        if isinstance(amount, str):
            amount = eval(amount)
            strat = stu_data['local_strategy']
            for pair in amount:
                if isinstance(pair, tuple):
                    if strat >= pair[0]:
                        amount = pair[1]
                        break
                else:
                    amount = pair
                    break
                
        this_goal = goal_descriptions[label]
        goal_text = _clean_excel(this_goal['Label'], stu_data, labels)
        goal_text = goal_text.replace('@',str(amount))
        goal_value = _eval_pdf_goal(label, stu_data, stu_apps)
        goal_result = eval(str(goal_value)+this_goal['Sign']+str(amount))
        if amount != 0:  # This allows variable goals to be zeroed for some students
            goal_eval.append([goal_text, str(goal_value),
                        ('Yes!' if goal_result else 'No')])
    
        # Finally, figure out the padding
        max_width = max([pdf.get_string_width(x[0]) for x in goal_eval])
        padtest =' '
        while (max_width + pdf.get_string_width(padtest)) < w:
            padtest += ' '
        pads = len(padtest) - 1
    return (pads, goal_eval)


def _eval_pdf_goal(goal_name, stu_data, stu_apps):
    """
    Lookup based function that returns analysis based on local student and
    apps tables, using a key from the settings file
    """
    if goal_name == 'il_public':
        return sum(stu_apps.local_ilpublic == 1)
    elif goal_name == 'il_match_plus':
        return sum((stu_apps.local_odds >= 50) &
                   (stu_apps.local_ilpublic == 1))
    elif goal_name == 'money_chicago':
        return sum((stu_apps.local_money == 1) &
                   (stu_apps.local_chilocal == 1))
    elif goal_name in ['total', 'lt_total']:
        return len(stu_apps)
    elif goal_name == 'reach':
        return sum((stu_apps.local_odds >= 20) &
                   (stu_apps.local_odds <  50))
    elif goal_name == 'match':
        return sum((stu_apps.local_odds >= 50) &
                   (stu_apps.local_odds <  80))
    elif goal_name == 'match_plus':
        return sum(stu_apps.local_odds >= 50)
    elif goal_name in ['safety', 'lt_safety']:
        return sum(stu_apps.local_odds >= 80)
    elif goal_name == 'lt_longshot_under':
        return sum(stu_apps.local_odds < 20)
    elif goal_name == 'money':
        return sum(stu_apps.local_money == 1)
    elif goal_name == 'lt_bad_money':
        return sum(stu_apps.local_money_code.isin(
                ['---','--','+/--','+/---']))
    elif goal_name == 'money_safety':
        return sum((stu_apps.local_money == 1) &
                   (stu_apps.local_odds >= 80))
    elif goal_name == 'tgr_plus':
        return sum(stu_apps.local_6yr_all_aah >= stu_data.local_target_gr)
    elif goal_name == 'money_tgr_plus_match_plus':
        return sum((stu_apps.local_6yr_all_aah >= stu_data.local_target_gr) &
                   (stu_apps.local_odds >= 50) &
                   (stu_apps.local_money == 1))
    elif goal_name == 'tgr_only':
        return sum((stu_apps.local_6yr_all_aah >= stu_data.local_target_gr) &
                   (stu_apps.local_6yr_all_aah < stu_data.local_ideal_gr))
    elif goal_name.startswith('money_tgr_only_'):
        if goal_name.endswith('reach_plus'):
            odds_target = 20
        elif goal_name.endswith('longshot_plus'):
            odds_target = 10
        return sum((stu_apps.local_6yr_all_aah >= stu_data.local_target_gr) &
                   (stu_apps.local_6yr_all_aah < stu_data.local_ideal_gr) &
                   (stu_apps.local_money == 1) &
                   (stu_apps.local_odds >= odds_target))
    elif goal_name == 'igr':
        return sum(stu_apps.local_6yr_all_aah >= stu_data.local_ideal_gr)
    elif goal_name.startswith('money_igr_'):
        if goal_name.endswith('reach_plus'):
            odds_target = 20
        elif goal_name.endswith('longshot_plus'):
            odds_target = 10
        return sum((stu_apps.local_6yr_all_aah >= stu_data.local_ideal_gr) &
                   (stu_apps.local_money == 1) &
                   (stu_apps.local_odds >= odds_target))
    elif goal_name == 'lt_far_below_tgr':
        return sum(stu_apps.local_6yr_all_aah < (stu_data.local_target_gr - .1))
    elif goal_name == 'national_louis':
        return sum(stu_apps.NCES == 147536)
    elif goal_name == 'golden_three':
        return sum((stu_apps.local_6yr_all_aah >= stu_data.local_target_gr) &
                   (stu_apps.local_odds >= 50) &
                   (stu_apps.local_money == 1))
    else:
        raise(RuntimeError('No code to evaluate goal label: '+name))