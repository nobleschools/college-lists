#!python3
'''Module for working with student records and making Students tab'''
import numpy as np
import pandas as pd
from reports_modules.excel_base import safe_write, write_array
from reports_modules.excel_base import make_excel_indices

DEFAULT_FROM_TARGET = 0.2 # default prediction below target grad rate
MINUS1_CUT = 0.2 # minimum odds required to "toss" a college in minus1 pred

def get_sat_translation(x, lookup_df):
    '''Apply function for calculating equivalent ACT for SAT scores.
    Lookup table has index of SAT with value of ACT'''
    sat = x
    if np.isreal(sat):
        if sat in lookup_df.index: # it's an SAT value in the table
            return lookup_df.loc[sat]
    return np.nan # default if not in table or not a number

def get_act_max(x):
    ''' Returns the max of two values if both are numbers, otherwise
    returns the numeric one or nan if neither is numeric'''
    act, sat_in_act = x
    if np.isreal(act):
        if np.isreal(sat_in_act):
            return max(act, sat_in_act)
        else:
            return act
    else:
        if np.isreal(sat_in_act):
            return sat_in_act
        else:
            return np.nan

def reduce_roster(campus, cfg, dfs, counselor,debug):
    '''Uses campus info and config file to reduce the active student list'''
    df = dfs['full_roster'].copy()
    if debug:
        print('Starting roster of {} students'.format(len(df)),
                flush=True,end='')
    if campus == 'All':
        df = df[df['Campus'].isin(cfg['all_campuses'])]
    else:
        df = df[df['Campus']==campus]
    if counselor != 'All':
        df = df.dropna(subset = ['Counselor'])
        df = df[df['Counselor'].str.contains(counselor)]
    if debug:
        print('..ending at {} students.'.format(len(df)),flush=True)

    # Two calculated columns need to be added for the application
    # analyses
    df['local_sat_in_act'] = df['SAT'].apply(get_sat_translation,
            args=(dfs['SATtoACT'],))
    df['local_act_max'] = df[['ACT','local_sat_in_act']].apply(
            get_act_max, axis=1)

    dfs['roster'] = df

def get_strategies(x,lookup_df):
    '''Apply function for calculating strategies based on gpa and act using the
    lookup table (mirrors Excel equation for looking up strategy'''
    gpa, act = x
    if np.isreal(gpa) and np.isreal(act):
        lookup = '{:.1f}:{:.0f}'.format(
                max(np.floor(gpa*10)/10,1.5), max(act, 12))
        return lookup_df['Strategy'].get(lookup,np.nan)
    else:
        return np.nan

def get_gr_target(x, lookup_strat, goal_type):
    '''Apply function to get the target or ideal grad rate for student'''
    strat, gpa, efc, race = x
    # 2 or 3 strategies are split by being above/below 3.0 GPA line
    # First we identify those and then adjust the lookup index accordingly
    special_strats = [int(x[0]) for x in lookup_strat.index if x[-1]=='+']
    if np.isreal(gpa) and np.isreal(strat):
        # First define the row in the lookup table
        strat_str = '{:.0f}'.format(strat)
        if strat in special_strats:
            lookup = strat_str + '+' if gpa >= 3.0 else strat_str + '<'
        else:
            lookup = strat_str 
        # Then define the column in the lookup table
        if efc == -1:
            column = 'minus1_' + goal_type
        elif race in ['W', 'A']:
            column = 'W/A_' + goal_type
        else:
            column = 'AA/H_' + goal_type
        return lookup_strat[column].get(lookup,np.nan)
    else:
        return np.nan

def adjust_odds(x):
    '''Apply function to adjust the odds within applications if the decision
    is already known. Also convert from 0-100 to 0-1'''
    odds, result = x
    if result == 'Accepted!':
        return 1.0
    elif result == 'Denied':
        return 0.0
    else:
        if np.isnan(odds):
            return odds
        else:
            return odds/100.0

def predict_perfect(grs, odds, default_gr, minus1=False):
    '''Calculates the "perfect prediction" by assuming students go to the
    highest grad rate school they get into. Can be used for "minus 1" by
    simply cutting the top school with odds > 20% (defined by constant)'''
    if minus1:
        # find the highest college with odds > MINUS1_CUT
        college_to_minus_out = -1
        for i in range(len(odds)):
            if odds.iloc[i] >= MINUS1_CUT:
                college_to_minus_out = i
                break
        if college_to_minus_out >= 0: # a college was found
            odds = odds.drop(odds.index[i])
            grs = grs.drop(grs.index[i])
    odds_left = 1.0 # Tracks the share of 100% left to hit
    expected_value_gr = 0.0 # will be built up cumulatively
    for i in range(len(grs)):
        this_college_odds = odds.iloc[i] * odds_left
        expected_value_gr += this_college_odds * grs.iloc[i]
        odds_left -= this_college_odds
        if not odds_left: # all of the possibilities are exhausted
            break
    return (expected_value_gr + odds_left * default_gr)

def predict_preference(grs, odds, default_gr, high_multiplier=2.0):
    '''Calculates predictions assuming students factor in grad rate
    with the highest grad rate school "high_multiplier" times more
    likely to be picked than the lowest and with colleges linearly
    distributed in preference by the grad rate between those extremes'''
    max_grad_rate = max(grs)
    min_grad_rate = min(grs)
    if max_grad_rate == min_grad_rate:
        return max_grad_rate
    expected_value_gr =0.0 # will be built up cumulatively
    weighted_sum = 0.0 # will be used to normalize the above
    for i in range(len(grs)):
        current_weight = odds.iloc[i] * ((grs.iloc[i] - min_grad_rate) / (
              max_grad_rate-min_grad_rate) * (high_multiplier - 1.0) + 1.0)
        weighted_sum += current_weight
        expected_value_gr += current_weight * grs.iloc[i]
    if weighted_sum < 1.0:
        expected_value_gr += (1.0 - weighted_sum) * default_gr
        weigthed_sum = 1.0
    return (expected_value_gr / weighted_sum)

def create_predictions(roster_df, app_df):
    '''iterates through the applications for each student to create predictions
    of most likely grad rate over multiple scenarios'''
    # Headers of return DataFrame
    return_table = [['StudentID','pred_perfect', 'pred_minus1',
                     'pred_some_pref', 'pred_all_equal']]

    for student in roster_df.index:
        # get all applications for the specific student
        s_app_df = app_df[app_df['hs_student_id'] == student].copy()
        if len(s_app_df) == 0:
                # No applications -> assume not going to college for now
                return_table.append([student]+[0.0]*4)
                continue
        choice_df = s_app_df[s_app_df['local_result']=='CHOICE!']
        if len(choice_df): # no need to predict if student has chosen
            choice_gr = choice_df['local_6yr_all_aah'].iloc[0]
            return_table.append([student]+[choice_gr]*4)
        else:
            # Now adjust the odds: 100% if accepted, 0% if denied
            s_app_df['local_odds_adj']=s_app_df[
                    ['local_odds','local_result']
                    ].apply(adjust_odds, axis=1)
            # Now only look at the subset of applications that are money
            # have a grad rate and have odds
            s_app_clean = s_app_df[(s_app_df['local_money']==1) &
                                   (s_app_df['local_odds_adj']>=0.0) &
                                   (s_app_df['local_6yr_all_aah']>=0.0)]
            if len(s_app_clean): # only calculate if some exist
                # This is the standard case for most students
                # create two pandas Series with the relevant data for calcs
                # (Note that these are sorted from highest gr to lowest)
                grs = s_app_clean['local_6yr_all_aah']
                odds = s_app_clean['local_odds_adj']
                default_gr = roster_df.loc[student,'local_target_gr']
                if np.isnan(default_gr):
                    default_gr = 0.0
                else:
                    default_gr = max(0.0, default_gr - DEFAULT_FROM_TARGET)
                prediction_perfect = predict_perfect(grs, odds, default_gr)
                prediction_minus1 = predict_perfect(
                        grs, odds, default_gr, minus1=True)
                prediction_somepref = predict_preference(
                        grs, odds, default_gr, 2.0)
                prediction_allequal = predict_preference(
                        grs, odds, default_gr, 1.0)

                return_table.append([student,
                    prediction_perfect,
                    prediction_minus1,
                    prediction_somepref, 
                    prediction_allequal])
            else:
                # No applications -> assume not going to college for now
                return_table.append([student]+[0.0]*4)

    return pd.DataFrame(return_table[1:],
                             columns=return_table[0]).set_index('StudentID')

def add_student_calculations(cfg, dfs, debug):
    '''Creates some calculated columns in the roster table'''
    df = dfs['roster'].copy()
    df['local_strategy'] = df[['GPA','local_act_max']].apply(get_strategies,
            axis=1, args=(dfs['Strategies'],))
    df['local_target_gr'] = df[
            ['local_strategy','GPA','EFC','Race/ Eth']].apply(
            get_gr_target, axis=1, args=(dfs['StudentTargets'],'target'))
    df['local_ideal_gr'] = df[
            ['local_strategy','GPA','EFC','Race/ Eth']].apply(
            get_gr_target, axis=1, args=(dfs['StudentTargets'],'ideal'))
    
    #after we've got target_gr, get the predictions
    # the returned df below should have same index as roster df w/ 4 columns
    prediction_df = create_predictions(df, dfs['apps'])
    df = pd.concat([df, prediction_df], axis=1)

    if debug:
        print(df.columns)

    dfs['roster'] = df

def push_column(columns, letters, label, formula, fmt,
                width, head_text, head_fmt, label_fmt, cond_format):
    '''Adds an item to a list of length 9 that define the columns with
    col0=Excel header, col1=label, col2=formula; replaces %label% with
    the corresponding letter in Excel for that letter plas a _r_,
    col3=format (data), col4=width, col5=header text (1st row),
    col6=header format, col7=label format (2nd row), col8=conditional format'''
    col_ltr = {x[1]:x[0] for x in columns}
    new_col = [letters[len(columns)],label]
    tokens = formula.split('%')
    for i in range(1,len(tokens),2):
        tokens[i] = col_ltr[tokens[i]]+'_r_'
    new_col.append(''.join(tokens))
    new_col.append(fmt)
    new_col.extend([width, head_text, head_fmt, label_fmt, cond_format])
    columns.append(new_col)
    return columns

def make_students_tab(writer, f_db, dfs, cfg, cfg_stu, campus, debug):
    '''Creates the Excel tab for students using cfg details'''
    if debug:
        print('Writing students tab...',flush=True,end='')
    df = dfs['roster']
    wb = writer.book
    sn = 'Students'
    ws = wb.add_worksheet(sn)

    # Now define a list of columns and how they are constructed

    master_cols = []
    col_letters = make_excel_indices()
    for stu_column in cfg_stu['students_columns']:
        for column_name in stu_column: # there's only one, but need to deref
            col = stu_column[column_name]
            if col['formula'].startswith('cfg:'):
                cfg_ref = col['formula'][4:]
                if campus in cfg[cfg_ref]:
                    formula = cfg[cfg_ref][campus]
                else:
                    formula = cfg[cfg_ref]['Standard']
            else:
                formula = col['formula']
            push_column(master_cols, col_letters, column_name,
                    formula, col['format'], col['width'],
                    col['head_text'], col['head_format'], col['label_format'],
                    col['cond_format'])
    
    # Now write the column headers:
    for i in range(len(master_cols)):
        col = master_cols[i]
        safe_write(ws,0,i,col[5],f_db[col[6]])
        safe_write(ws,1,i,col[1],f_db[col[7]])

    # Do the data columns:
    start_row = 2
    end_row = len(df) + 1
    end_col = len(master_cols)-1

    row = start_row
    for i, stu_data in df.iterrows():
        sr = str(row+1)
        for c in range(len(master_cols)):
            letter, label, formula, fmt = master_cols[c][:4]
            if formula.startswith('tbl:'):
                data_name = formula[4:]
                safe_write(ws, row, c, stu_data[data_name],f_db[fmt])
            elif formula.startswith('<id>'):
                safe_write(ws, row, c, i, f_db[fmt])
            elif formula.startswith('{'):
                write_array(ws, row, c, formula.replace('_r_', sr), f_db[fmt])
            else:
                safe_write(ws, row, c, formula.replace('_r_', sr), f_db[fmt])
        row += 1

    # Add Names
    col_ltr = {x[1]:x[0] for x in master_cols}
    for name, label in cfg_stu['student_names'].items():
        col = col_ltr[label]
        wb.define_name(name,'='+sn+'!$'+col+'$'+str(start_row+1)+':$'+
                col+'$'+str(end_row+1))

    # Do the conditional formating underlines
    for i in range(len(master_cols)):
        ws.conditional_format(start_row, i, end_row, i,
            {'type':'formula', 'criteria': '=IF(MOD(ROW()-2,4)=0,TRUE,FALSE)',
                'format':f_db[master_cols[i][8]]})

    # Set widths:
    for i in range(len(master_cols)):
        width = master_cols[i][4]
        if isinstance(width, str): # an 'h' was appended to the width
            ws.set_column(i,i,float(width[:-1]),f_db['yellow'],{'hidden':True})
        else:
            ws.set_column(i,i,width)
    
    # Finally, the rest of the tab's formatting
    ws.set_row(1,52)
    ws.autofilter(start_row-1,0, end_row, end_col)
    ws.freeze_panes(start_row,7)
    if debug:
        print('Done!',flush=True)
