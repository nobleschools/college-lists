#!python3
'''Module for working with single student reports'''
from reports_modules.excel_base import safe_write

def make_single_tab(writer, f_db, dfs, cfg, cfg_ssv, campus, debug, blank=True):
    """
    Creates the Excel tab for single student report using cfg details
    If blank, then doesn't use the applications from that table.
    As a whole, this tab is the most prescriptive about spacing and content
    At some point there may be more opportunity to customize via yaml file
    """

    # First initialize inputs
    if debug:
        out_str = '(blank) ' if blank else ''
        print('Writing single student '+out_str+'tab...',flush=True,end='')
    #df = dfs['roster']
    wb = writer.book
    sn = 'SingleStudentView' + ('Blank' if blank else '')
    ws = wb.add_worksheet(sn)
    first_student = dfs['roster']['LastFirst'].iloc[0]
    
    # Next read when the row types start and stop from the cfg file
    if blank:
        row_info = cfg_ssv['row_info']['Blank']
    elif campus in cfg_ssv['row_info']:
        row_info = cfg_ssv['row_info'][campus]
    else:
        row_info = cfg_ssv['row_info']['Standard']

    b_start = row_info['blank_start'] # generally row 8
    b_end = row_info['blank_end']
    s_start = row_info['student_start']
    s_end = row_info['student_end']
    d_start = b_start if b_start else s_start #start of all data
    d_end = s_end if s_end else b_end #end of all data

    # Read in specifications for the upper right header
    if campus in cfg_ssv['counselor_header']:
        top_header = cfg_ssv['counselor_header'][campus]
    else:
        top_header = cfg_ssv['counselor_header']['Standard']

    # Write the hidden stuff at the left (in the header)
    safe_write(ws, 1, 2, '=INDEX(KidIDs,D2)', f_db['ssv_yellow'])
    safe_write(ws, 1, 3, 1, f_db['ssv_yellow'])
    safe_write(ws, 2, 2, 'Student#', f_db['ssv_yellow'])
    safe_write(ws, 2, 3, '=INDEX(KidIDs,MATCH(E3,LastFirst,0))',
            f_db['ssv_yellow'])
    safe_write(ws, 3, 2, '#apps', f_db['ssv_yellow'])
    safe_write(ws, 3, 3, '=INDEX(Apps,MATCH(D3,KidIDs,0))', f_db['ssv_yellow'])
    safe_write(ws, 4, 2, 'firstRow', f_db['ssv_yellow'])
    safe_write(ws, 4, 3, '=MATCH(D3,Students,0)', f_db['ssv_yellow'])
    safe_write(ws, 5, 0, '=INDEX(ReachStudentTargets,MATCH(D3,KidIDs,0))',
            f_db['ssv_yellow_percent'])
    safe_write(ws, 5, 1, '=D6', f_db['ssv_yellow_percent'])
    safe_write(ws, 5, 2, 'Target', f_db['ssv_yellow'])
    safe_write(ws, 5, 3, '=INDEX(StudentTargets,MATCH(D3,KidIDs,0))',
            f_db['ssv_yellow_percent'])

    # Write the header at the top
    safe_write(ws, 0, 4, '=IF(ISNUMBER(D3),'+
    '"College application odds report for "&INDEX(KidFirst,MATCH(D3,KidIDs,0))'+
    '&" "&INDEX(KidLast,MATCH(D3,KidIDs,0)),"SELECT YOUR NAME")',
    f_db['ssv_title'])
    if not blank:
        if campus in cfg_ssv['print_header']: # only do this if spec'ed
            safe_write(ws, 0, 5, cfg_ssv['print_header'][campus],
                    f_db['ssv_date'])
        ws.merge_range(0, 8, 0, 9, top_header, f_db['ssv_counselor_title'])
    safe_write(ws, 1, 4, "Select student's name:",
            f_db['ssv_student_prompt'])
    safe_write(ws, 2, 4, first_student, f_db['ssv_select_student'])

    ws.data_validation(2,4, 2,4, {'validate': 'list',
                             'source': '=LastFirst'})

    safe_write(ws, 3, 4, 'Odds of 1 or more acceptances to:',
            f_db['ssv_odds_title'])
    safe_write(ws, 4, 4, '="""Money"" "&TargetGRLabel&" grade rate ("'+
    '&TGRshortLabel&") or better schools"',
            f_db['ssv_mtgr_label'])
    safe_write(ws, 5, 4, '="""Money"" "&IdealGRLabel&" grade rate ("'+
    '&IGRshortLabel&") or better schools"',
            f_db['ssv_migr_label'])

    safe_write(ws, 1, 5, 'ACT/SAT', f_db['ssv_act_title'])
    safe_write(ws, 2, 5, '=INDEX(ActualACT,MATCH(D3,KidIDs,0))&"/"&'+
            'INDEX(ActualSAT,MATCH(D3,KidIDs,0))', f_db['ssv_act'])
    safe_write(ws, 3, 5, '=INDEX(KidACTs,MATCH(D3,KidIDs,0))',
            f_db['ssv_odds_title_b'])
    safe_write(ws, 5, 5, '', f_db['ssv_migr_label_b'])

    safe_write(ws, 1, 6, 'GPA', f_db['ssv_gpa_title'])
    safe_write(ws, 2, 6, '=INDEX(KidGPAs,MATCH(D3,KidIDs,0))',
            f_db['ssv_gpa'])
    safe_write(ws, 3, 6, '', f_db['ssv_odds_title_c'])
    safe_write(ws, 4, 6, '=1-PRODUCT(AF'+str(d_start+1)+
            ':AF'+str(d_end+1)+')', f_db['ssv_mtgr'])
    safe_write(ws, 5, 6, '=1-PRODUCT(AG'+str(d_start+1)+
            ':AG'+str(d_end+1)+')', f_db['ssv_migr'])

    safe_write(ws, 1, 7, 'Race/Eth', f_db['ssv_race_title'])
    safe_write(ws, 2, 7, '=INDEX(KidRace,MATCH(D3,KidIDs,0))',
            f_db['ssv_race'])
    safe_write(ws, 3, 7, 'Goals for #s to the left:',
            f_db['ssv_odds_title'])
    safe_write(ws, 4, 7, '="<--Shoot for at least 90% for Money "'+
               '&TGRshortLabel', f_db['ssv_mtgr_label'])
    safe_write(ws, 5, 7, '="<--Shoot for at least 50% for Money "'
               '&IGRshortLabel', f_db['ssv_migr_label'])
    
    safe_write(ws, 1, 8, 'IGR', f_db['ssv_igr_title'])
    safe_write(ws, 2, 8, 'TGR', f_db['ssv_tgr_title'])
    safe_write(ws, 3, 8, '', f_db['ssv_odds_title_b'])
    safe_write(ws, 5, 8, '', f_db['ssv_migr_label_b'])

    safe_write(ws, 1, 9, '=INDEX(ReachStudentTargets,MATCH(D3,KidIDs,0))',
            f_db['ssv_igr'])
    safe_write(ws, 2, 9, '=INDEX(StudentTargets,MATCH(D3,KidIDs,0))',
            f_db['ssv_tgr'])
    safe_write(ws, 3, 9, '', f_db['ssv_odds_title_c'])
    safe_write(ws, 4, 9, '', f_db['ssv_mtgr'])
    safe_write(ws, 5, 9, '', f_db['ssv_migr'])

    # Now write the blank rows--first the header row
    safe_write(ws, 7, 4, 'Schools you might apply to:',
            f_db['ssv_schools_blank_prompt'])
    safe_write(ws, 7, 5, '=IF(OR(H3="H",H3="B"),"6 yr AA/H Grad Rate",'+
            '"6 yr (all) Grad Rate")', f_db['ssv_blank_title'])
    safe_write(ws, 7, 6, 'Odds of Admit',
            f_db['ssv_blank_title'])
    safe_write(ws, 7, 7, 'For you, school is a',
            f_db['ssv_blank_title_small'])
    safe_write(ws, 7, 8, 'App Status',
            f_db['ssv_blank_title'])
    safe_write(ws, 7, 9, 'Award code',
            f_db['ssv_blank_title'])
    safe_write(ws, 7, 10, 'Comp tier', f_db['ssv_color_1'])
    safe_write(ws, 7, 11, 'MoneyYesNo', f_db['ssv_color_1'])
    safe_write(ws, 7, 12, 'ACT25', f_db['ssv_color_2'])
    safe_write(ws, 7, 13, 'GPA', f_db['ssv_color_3'])
    safe_write(ws, 7, 14, 'ACT', f_db['ssv_color_3'])
    safe_write(ws, 7, 15, 'GPAcoefB', f_db['ssv_color_4'])
    safe_write(ws, 7, 16, 'ACTcoefB', f_db['ssv_color_4'])
    safe_write(ws, 7, 17, 'InterceptB', f_db['ssv_color_4'])
    safe_write(ws, 7, 18, 'LogitB', f_db['ssv_color_4'])
    safe_write(ws, 7, 19, 'GPAcoefA', f_db['ssv_color_5'])
    safe_write(ws, 7, 20, 'ACTcoefA', f_db['ssv_color_5'])
    safe_write(ws, 7, 21, 'InterceptA', f_db['ssv_color_5'])
    safe_write(ws, 7, 22, 'LogitA', f_db['ssv_color_5'])
    safe_write(ws, 7, 23, 'FinalLogit', f_db['ssv_color_5'])
    safe_write(ws, 7, 24, 'Odds', f_db['ssv_color_5'])
    safe_write(ws, 7, 25, 'Class', f_db['ssv_color_5'])
    safe_write(ws, 7, 26, 'MGROrBetter', f_db['ssv_color_4'])
    safe_write(ws, 7, 27, 'RGROrBetter', f_db['ssv_color_4'])
    safe_write(ws, 7, 28, 'InverseOdds', f_db['ssv_color_4'])

    ds = str(d_start+1)
    de = str(d_end+1)
    safe_write(ws, 5, 29, '=COUNTIF(AD'+ds+':AD'+de+',"<1")')
    safe_write(ws, 5, 30, '=COUNTIF(AE'+ds+':AE'+de+',"<1")')
    safe_write(ws, 5, 31, '=COUNTIF(AF'+ds+':AF'+de+',"<1")')
    safe_write(ws, 5, 32, '=COUNTIF(AG'+ds+':AG'+de+',"<1")')

    safe_write(ws, 7, 29, 'MGRMult')
    safe_write(ws, 7, 30, 'RGRMult')
    safe_write(ws, 7, 31, 'MGRMoney')
    safe_write(ws, 7, 32, 'RGRMoney')

    # Then loop through and print the blank rows
    for r in range(b_start, b_end+1):
        r_excel = str(r+1)
        if r == b_start: # the first row has a different reference
            safe_write(ws, r, 0, "=A6", f_db['ssv_yellow_percent'])
            safe_write(ws, r, 1, "=B6", f_db['ssv_yellow_percent'])
            safe_write(ws, r, 2, "=ROW()", f_db['ssv_yellow'])
        else:
            safe_write(ws, r, 0, "=A"+str(r), f_db['ssv_yellow_percent'])
            safe_write(ws, r, 1, "=B"+str(r), f_db['ssv_yellow_percent'])
        safe_write(ws, r, 3, '=INDEX(ExtraCollegeNCES,MATCH(E'+r_excel+
                ',ExtraCollegeChoice,0))', f_db['ssv_yellow'])
        safe_write(ws, r, 4, "", f_db['ssv_select_college'])
        ws.data_validation(r,4, r,4, {'validate': 'list',
                             'source': '=ExtraCollegeChoice'})
        safe_write(ws, r, 5, '=IF(ISERROR(D'+r_excel+
                '),"",INDEX(IF(OR(H3="H",H3="B"),AllCollegeAAHGR,'+
                'AllCollegeGR),MATCH(D'+r_excel+
                ',AllCollegeNCES,0)))', f_db['ssv_gr'])
        safe_write(ws, r, 6, '=IF(ISERROR(D'+r_excel+
                '),"",IF(ISNUMBER(Y'+r_excel+'),Y'+r_excel+'/100,"N/A"))',
                f_db['ssv_gr'])
        safe_write(ws, r, 7, '=IF(ISERROR(D'+r_excel+'),"",Z'+r_excel+')',
                f_db['ssv_gr'])
        safe_write(ws, r, 8, '=IF(ISERROR(D'+r_excel+'),"","N/A")',
                f_db['ssv_gr'])
        safe_write(ws, r, 9, '=IF(ISERROR(D'+r_excel+
                '),"",INDEX(AllCollegeMoneyCode,MATCH(D'+r_excel+
                ',AllCollegeNCES,0)))', f_db['ssv_gr'])
        safe_write(ws, r, 10,'=INDEX(AllCollegeBarrons,MATCH(D'+r_excel+
                ',AllCollegeNCES,0))')
        safe_write(ws, r, 11,'=IF(ISERROR(D'+r_excel+
                '),"",INDEX(AllCollegeMoney,MATCH(D'+r_excel+
                ',AllCollegeNCES,0)))')
        safe_write(ws, r, 12,'=INDEX(AllCollegeACT25,MATCH(D'+r_excel+
                ',AllCollegeNCES,0))')
        safe_write(ws, r, 13,'=G3')
        safe_write(ws, r, 14,'=F4')
        safe_write(ws, r, 15,'=INDEX(CustomWeightsGPA,MATCH($H3&":"&$D'+
                r_excel+',CustomWeightsIndex,0))')
        safe_write(ws, r, 16,'=INDEX(CustomWeightsACT,MATCH($H3&":"&$D'+
                r_excel+',CustomWeightsIndex,0))')
        safe_write(ws, r, 17,'=INDEX(CustomWeightsIntercept,MATCH($H3&":"&$D'+
                r_excel+',CustomWeightsIndex,0))')
        safe_write(ws, r, 18,'=P'+r_excel+'*N'+r_excel+'+Q'+r_excel+
                '*O'+r_excel+'+R'+r_excel+'')
        safe_write(ws, r, 19,'=INDEX(CoefficientsGPA,MATCH($H3&":"&$K'+
                r_excel+',CoefficientsIndex,0))')
        safe_write(ws, r, 20,'=INDEX(CoefficientsACT,MATCH($H3&":"&$K'+
                r_excel+',CoefficientsIndex,0))')
        safe_write(ws, r, 21,'=INDEX(CoefficientsIntercept,MATCH($H3&":"&$K'+
                r_excel+',CoefficientsIndex,0))')
        safe_write(ws, r, 22,'=T'+r_excel+'*N'+r_excel+'+(O'+r_excel+
                '-M'+r_excel+')*U'+r_excel+'+V'+r_excel+'')
        safe_write(ws, r, 23,'=IF(ISNUMBER(S'+r_excel+'),S'+r_excel+
                ',W'+r_excel+')')
        safe_write(ws, r, 24,'=IF(ISNUMBER(X'+r_excel+'),IF(AND(T'+r_excel+
                '=1,U'+r_excel+'=1,V'+r_excel+'=1),100,100*EXP(X'+r_excel+
                ')/(1+EXP(X'+r_excel+'))),"N/A")')
        safe_write(ws, r, 25,'=IF(ISNUMBER(Y'+r_excel+'),IF(Y'+r_excel+
                '>=99,SureThingLabel,IF(Y'+r_excel+'>=95,SecureLabel,IF(Y'
                +r_excel+'>=80,SafetyLabel,IF(Y'+r_excel+'>=50,MatchLabel,IF(Y'
                +r_excel+'>=20,ReachLabel,IF(Y'+r_excel+
                '>=10,LongshotLabel,HailMaryLabel)))))),"Other")')
        safe_write(ws, r, 26,'=IF($F'+r_excel+'>=J$3,1,0)')
        safe_write(ws, r, 27,'=IF($F'+r_excel+'>=J$2,1,0)')
        safe_write(ws, r, 28,'=IF(ISNUMBER(Y'+r_excel+'),1-Y'+r_excel+'/100,1)')
        safe_write(ws, r, 29,'=IF(AA'+r_excel+'=1,AC'+r_excel+',1)')
        safe_write(ws, r, 30,'=IF(AB'+r_excel+'=1,AC'+r_excel+',1)')
        safe_write(ws, r, 31,'=IF(L'+r_excel+'=1,AD'+r_excel+',1)')
        safe_write(ws, r, 32,'=IF(L'+r_excel+'=1,AE'+r_excel+',1)')

    # Next, if not blank, do the student specific headers and rows
    if not blank:
        # Do the header
        r = s_start - 1
        r_excel = str(s_start)
        safe_write(ws, r, 4, 'Schools currently applying to ("*" indicates '+
                'prospective):',f_db['ssv_schools_blank_prompt'])
        safe_write(ws, r, 5, '=IF(OR(H3="H",H3="B"),"6 yr AA/H Grad Rate",'+
            '"6 yr (all) Grad Rate")', f_db['ssv_blank_title_right'])
        safe_write(ws, r, 6, 'Odds of Admit',f_db['ssv_blank_title'])
        safe_write(ws, r, 7, 'For you, school is a',
            f_db['ssv_blank_title_small_right'])
        safe_write(ws, r, 8, 'App Status',f_db['ssv_blank_title_right'])
        safe_write(ws, r, 9, 'Award code',f_db['ssv_blank_title'])
        for col in range(29,33):
            safe_write(ws, r, col, 1)
        ws.set_row(r,30.0)

        # Do the data rows
        for r in range(s_start, s_end+1):
            r_excel = str(r+1)
            if r == s_start: # the first row has a different reference
                safe_write(ws, r, 0, '=A'+str(b_end+1),
                        f_db['ssv_yellow_percent'])
                safe_write(ws, r, 1, '=B'+str(b_end+1),
                        f_db['ssv_yellow_percent'])
                safe_write(ws, r, 2, '=ROW()-1', f_db['ssv_yellow'])
            else:
                safe_write(ws, r, 0, '=A'+str(r), #reference row above
                        f_db['ssv_yellow_percent'])
                safe_write(ws, r, 1, '=B'+str(r),
                        f_db['ssv_yellow_percent'])
                safe_write(ws, r, 2, '=C'+str(r),
                        f_db['ssv_yellow'])
            safe_write(ws, r, 3, '=IF((ROW()-C'+r_excel+')<=D4,D5+(ROW()-C'
                    +r_excel+'-1),"")', f_db['ssv_yellow'])
            safe_write(ws, r, 4, '=IF(ISNUMBER(D'+r_excel+
                    '),INDEX(CollegeNames,D'+r_excel+'),"")')
            safe_write(ws, r, 5, '=IF(ISNUMBER(D'+r_excel+
                    '),INDEX(IF(OR(H3="H",H3="B"),GradRates,AllGradRates),D'
                    +r_excel+'),"")', f_db['ssv_gr'])
            safe_write(ws, r, 6, '=IF(ISNUMBER(D'+r_excel+
                    '),IF(ISNUMBER(INDEX(Odds,D'+r_excel+')),INDEX(Odds,D'
                    +r_excel+')/100,"N/A"),"")', f_db['ssv_gr'])
            safe_write(ws, r, 7, '=IF(ISNUMBER(D'+r_excel+'),INDEX(Classes,D'
                    +r_excel+'),"")', f_db['ssv_gr'])
            safe_write(ws, r, 8, '=IF(ISNUMBER(D'+r_excel+'),INDEX(Results,D'
                    +r_excel+'),"")', f_db['ssv_gr'])
            safe_write(ws, r, 9, '=IFERROR(IF(ISNUMBER(D'+r_excel+
                    '),INDEX(AllCollegeMoneyCode,MATCH(INDEX(NCESids,D'+
                    r_excel+'),AllCollegeNCES,0)),""),"N/A")', f_db['ssv_gr'])
            for c, t in [(29,'MGRMult'), # do the final four columns
                         (30,'RGRMult'),
                         (31,'MGRMoneyMult'),
                         (32,'RGRMoneyMult')]:
                safe_write(ws, r, c, '=IF(ISNUMBER(D'+r_excel+
                        '),INDEX('+t+',D'+r_excel+'),1)')

        # If present, do the custom formatting and goals box
        
        #Trip quote here if using old way
        if campus in cfg_ssv['school_goals']:
            safe_write(ws, s_end+1, 4, 'Your list compared to campus goals:',
                    f_db['ssv_goals_intro'])
            safe_write(ws, s_end+2, 4, 'Campus Goal',
                    f_db['ssv_goals_t1'])
            safe_write(ws, s_end+2, 5, 'You',
                    f_db['ssv_goals_t2'])
            ws.merge_range(s_end+2, 6, s_end+2, 7, 'Met?',
                    f_db['ssv_goals_t3'])
            g_start = s_end+3
            # Now loop through the goals, checking for size so we can
            # do special formating for the end goal
            campus_goals = cfg_ssv['school_goals'][campus].copy()
            for i in range(len(campus_goals)):
                r_excel = str(g_start+i+1)
                label, amount = campus_goals[i].popitem()
                
                # Goals are usually integers, but there can be extra logic
                if isinstance(amount, str):
                    amount = eval(amount)
                    detailed_goal = True
                else:
                    detailed_goal = False
                
                this_goal = cfg_ssv['goal_descriptions'][label]
                
                # First, do the hidden goal number in column D
                if detailed_goal:
                    # This will handle a list with some tuples and ending with
                    # an integer. The tuples have Strategy->N structure and
                    # are in descending order of strategy
                    goal_formula = '=@'
                    for x in amount:
                        if isinstance(x, tuple):
                            strat_limit, strat_goal = x
                            goal_formula = goal_formula.replace('@',
                                'IF(INDEX(Strats,MATCH(D3,KidIds,0))>='+
                                str(strat_limit)+','+str(strat_goal)+',@)')
                        else:
                            goal_formula = goal_formula.replace('@',str(x))
                    safe_write(ws, g_start+i, 3, goal_formula)
                else:
                    safe_write(ws, g_start+i, 3, amount)
                
                goal_fmt = ['ssv_goal_text','ssv_goal_eval','ssv_goal_result']
                if i == (len(campus_goals) - 1):
                    #special end formats for last row of goals
                    goal_fmt = [goal+'_end' for goal in goal_fmt]
                
                safe_write(ws, g_start+i, 4, # goal text (Col E)
                           this_goal['Label'].replace('@','"&D'+r_excel+'&"'),
                           f_db[goal_fmt[0]])
                safe_write(ws, g_start+i, 5, # student comp (Col F)
                           this_goal['Eval'],
                           f_db[goal_fmt[1]])
                ws.merge_range(g_start+i, 6, g_start+i, 7, #assessment (Col G)
                               '=IF(F'+r_excel+this_goal['Sign']+
                               'D'+r_excel+',"Yes!","No")',
                               f_db[goal_fmt[2]])
             
        # TODO: Maybe make this a strict if versus elif--check spacing
        elif campus in cfg_ssv['print_footer']: # only do this if spec'ed
            safe_write(ws, 37, 4, cfg_ssv['print_footer'][campus],
                    f_db['ssv_footer'])
            for c in range(5,10):
                safe_write(ws, 37, c, '', f_db['ssv_footer'])

    # Finally, the rest of the tab's formatting (rows/columns)
    cond_ranges = [('$F$'+str(b_start+1)+':$F$'+str(b_end+1), str(b_start+1))]
    if s_start: # student specific section exists
        cond_ranges.append(('$F$'+str(s_start+1)+':$F$'+str(s_end+1),
            str(s_start+1)))
        ws.conditional_format('$I$'+str(s_start+1)+':$I$'+str(s_end+1)
                        , {'type': 'formula',
                        'criteria': '=IF(I'+str(s_start+1)+'<>"",TRUE,FALSE)',
                        'format': f_db['ssv_cond_non_empty']})
    for cond_range, i_row in cond_ranges:
        ws.conditional_format(cond_range, {'type': 'formula',
                        'criteria': '=IF(F'+i_row+'>=A'+i_row+',TRUE,FALSE)',
                        'format': f_db['ssv_cond_blue_bold']})
        ws.conditional_format(cond_range, {'type': 'formula',
                        'criteria': '=IF(F'+i_row+'<B'+i_row+',TRUE,FALSE)',
                        'format': f_db['ssv_cond_red_grey']})
        #ADD BARS FOR OTHER COLUMNS
        ws.conditional_format(cond_range, {'type': 'formula',
                        'criteria': '=IF(F'+i_row+'<>"",TRUE,FALSE)',
                        'format': f_db['ssv_cond_non_empty']})
    ws.set_row(0,19.5)
    ws.set_row(2,15.75)
    ws.set_row(5,15.75)
    ws.set_row(6,6.0)
    ws.set_row(7,30.0)
    ws.set_column(0,3,8.0,f_db['ssv_yellow'],{'hidden':True})
    ws.set_column(4,4,40.29)
    ws.set_column(5,5,9.0)
    ws.set_column(6,6,6.86)
    ws.set_column(7,7,8.14)
    ws.set_column(8,8,8.86)
    ws.set_column(9,9,18.00)
    ws.set_column(10,28,7.00,f_db['ssv_color_1'],{'hidden':True})
    ws.set_column(29,32,7.00,f_db['ssv_color_6'],{'hidden':True})

    ws.set_margins(left=0.5,right=0.5,top=0.75,bottom=0.75)
    if 'aspect' in row_info: # there's a specification for portrait/landscape
        if row_info['aspect'] == 'landscape':
            ws.set_landscape()

    if not blank:
        ws.freeze_panes(s_start,0)
        for r in range(b_start+1, b_end+1):
            ws.set_row(r, None, None, {'level': 2})

    if debug:
        print('Done!',flush=True)
