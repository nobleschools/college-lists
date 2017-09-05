#!python3
'''Module for creating the applications tab (with Excel formulas)'''
import numpy as np
import pandas as pd
from reports_modules.excel_base import safe_write, make_excel_indices

def lookup_source_field(x,source_df,field,default='N/A', force_na=False):
    '''Utility function to map values from source df to a series
    in the apps table'''
    if pd.isnull(x):
        return np.nan
    else:
        return_value = source_df[field].get(x,default)
        if force_na:
            return default if return_value == force_na else return_value
        else:
            return return_value

def round2(x):
    '''Utility function to round to nearest hundreth'''
    return round(x, 2)

def all_ones(x):
    '''Utility function to check if all (3) elements all equal 1'''
    return all(n == 1 for n in x)

def calc6yr(args):
    '''Calculates the final 6yr grad rate based on the baseline grad rate
    and whether the college gets a "bump" for being a partner, where
    bump is either 15% or half the distance to 100%, whichever smaller'''
    gr, partner_bump = args
    if np.isnan(gr):
        return 0
    else:
        if partner_bump:
            return round(gr + min(0.15, (1-gr)/2), 2)
        else:
            return round(gr, 2)

def get_result(args):
    '''Calculates a limited result code for use in generating predictions'''
    result_code, attending = args
    if result_code == 'denied':
        return 'Denied'
    elif result_code in ['accepted', 'cond. accept', 'summer admit']:
        if attending == 'yes':
            return 'CHOICE!'
        else:
            return 'Accepted!'
    else:
        return 'Pending'

def reduce_and_augment_apps(cfg, dfs, debug):
    '''Restrict an applications table to those apps for students in roster
    then add lookup and calculated fields, finally sorting for output'''
    # A. first reduce
    df = dfs['applications']
    id_list = set(dfs['roster'].index)
    df = df[df['hs_student_id'].isin(id_list)].copy()

    # B. then add lookup columns
    # B.1. first from the student roster
    # The below specifies target label, source label, n/a value
    roster_fields = [('local_gpa', 'GPA', np.nan),
                     ('local_act', 'ACT', np.nan),
                     ('local_race','Race/ Eth', 'TBD'),
                     ]
    for local_label, roster_label, na_val in roster_fields:
        df[local_label] = df['hs_student_id'].apply(lookup_source_field,
            args=(dfs['roster'],roster_label, na_val, 'TBD'))

    # B.2. second from college table
    college_fields = [('local_barrons', 'SimpleBarrons', 'N/A'),
                      ('local_act_25', 'AdjACT25', np.nan),
                      ('local_act_50', 'AdjACT50', np.nan),
                      ('local_money', 'MoneyYesNo', 0),
                      ('local_6yr_all', 'Adj6yrGrad_All', np.nan),
                      ('local_6yr_aah', 'Adj6yrGrad_AA_Hisp', np.nan),
                      ]
    for local_label, college_label, na_val in college_fields:
        df[local_label] = df['NCES'].apply(lookup_source_field,
                args=(dfs['AllColleges'], college_label, na_val))
    
    # B.3. third from the standard odds table
    weights_fields = [('local_gpa_ca', 'GPAcoef'),
                      ('local_act_ca', 'ACT-coef'),
                      ('local_inta', 'Intercept'),
                      ]
    coef_index = df['local_race'] + ':' + df['local_barrons']
    for local_label, coef_label in weights_fields:
        df[local_label] = coef_index.apply(lookup_source_field,
                args=(dfs['StandardWeights'], coef_label, np.nan))

    cweights_fields = [('local_gpa_cb', 'GPAcoef'),
                      ('local_act_cb', 'ACTcoef'),
                      ('local_intb', 'Intercept'),
                      ]
    coef_index = df['local_race'] + ':' + df['NCES'].apply(str)
    for local_label, coef_label in cweights_fields:
        df[local_label] = coef_index.apply(lookup_source_field,
                args=(dfs['CustomWeights'], coef_label, np.nan))



    # C. then add calculated columns (for use internal use, not publishing)
    # the next row picks "act 25" if race is "H" or "B" and "act 50 otherwise
    df['local_act_25_50'] = df['local_act_25'].where(
            df['local_race'].isin(['H','B']), df['local_act_50'])
    df['local_logita'] = (
            df['local_gpa_ca']*df['local_gpa']+
            (df['local_act']-df['local_act_25_50'])*df['local_act_ca']+
            df['local_inta'])
    df['local_logitb'] = (
            df['local_gpa_cb']*df['local_gpa']+
            df['local_act_cb']*df['local_act']+
            df['local_intb'])
    # For community colleges, the "a" method for logit has coefficients
    # equal to exactly 1 for all three coefficients. In this special
    # case, the odds should automatically be 100
    df['local_auto100'] = df[['local_gpa_ca',
                              'local_act_ca',
                              'local_inta']].apply(all_ones, axis=1)
    df['local_final_logit'] = df['local_logitb'].where(
            pd.notnull(df['local_logitb']), df['local_logita'])
    df['local_odds_calc'] = (100*np.exp(df['local_final_logit'])/(
            1+np.exp(df['local_final_logit']))).apply(round2)
    # the next line assigns odds_calc unless auto100 is true
    df['local_odds'] = df['local_odds_calc'].where(
            ~df['local_auto100'], 100)

    # all of the above are for odds, but a handful of other columns need
    # to be calculated
    df['local_6yr_all_aah_temp'] = df['local_6yr_aah'].where(
            df['local_race'].isin(['H','B']), df['local_6yr_all'])
    # before completing the above, we need to check whether the school
    # gets a partner "bump" and then round
    df['local_partner_bump'] = df['comments'] == 'Posse'
    df['local_6yr_all_aah'] = df[['local_6yr_all_aah_temp',
                          'local_partner_bump']].apply(calc6yr, axis=1)

    df['local_result']=df[['result_code','attending']].apply(get_result, axis=1)

    if debug:
        print(df.columns)

    # D. finally sort
    dfs['apps'] = df.sort_values(['Campus','hs_student_id',
        'local_6yr_all_aah'], ascending=[True, True, False])

def push_column(columns, letters, label, formula, fmt=None):
    '''Adds an item to a list of length 3 lists that define columns with
    col0=Excel header, col1=label, col2=formula; replaces %label% with
    the corresponding letter in Excel for that letter plus a _r_'''
    col_ltr = {x[1]:x[0] for x in columns}
    new_col = [letters[len(columns)],label]
    tokens = formula.split('%')
    for i in range(1,len(tokens),2):
        tokens[i] = col_ltr[tokens[i]]+'_r_'
    new_col.append(''.join(tokens))
    new_col.append(fmt)
    columns.append(new_col)
    return columns

def make_apps_tab(writer, f_db, dfs, cfg, cfg_app, debug):
    '''Creates the Excel tab for applications only for students in roster'''
    if debug:
        print('Writing applications tab...',flush=True,end='')

    df = dfs['apps']
    wb = writer.book
    sn = 'Applications'
    ws = wb.add_worksheet(sn)

    # Now define a list of columns and how they are constructed

    # First the columns that are direct from the df
    cols = cfg_app['app_fields']
    col_letters = make_excel_indices() # column headers used in Excel
    current_use = ['use_df']*len(cols)
    fmts = [None]*len(cols)
    master_cols = [list(a) for a in zip(col_letters,cols,current_use,fmts)]

    format_catch = cfg_app['app_format_catch'] # for coloring df fields
    for x in master_cols:
        if x[1] in format_catch:
            x[3] = format_catch[x[1]]

    # Second define the calculated columns
    for app_column in cfg_app['applications_calculations']:
        for column_name in app_column: # there's only one, but need to deref
            formula = app_column[column_name]['formula']
            fmt = app_column[column_name]['format']
            push_column(master_cols, col_letters,
                    column_name, formula, fmt)

    # Now write the column headers:
    for i in range(len(master_cols)):
        col = master_cols[i]
        ws.write(0,i,col[1],f_db[(col[3] if col[3] else 'bold')])

    # Write data based on master_cols key
    start_row = 1
    end_row = len(df)
    end_col = len(master_cols)-1

    row = start_row
    for i, app_data in df.iterrows():
        sr = str(row+1)
        for c in range(len(master_cols)):
            letter, label, formula, fmt = master_cols[c]
            if formula == 'use_df':
                safe_write(ws, row, c, app_data[label],n_a='N/A')
            else:
                safe_write(ws, row, c, formula.replace('_r_',sr))
        row += 1

    # Do names
    col_ltr = {x[1]:x[0] for x in master_cols}
    for name, label in cfg_app['application_names'].items():
    #for [name,label] in name_list:
        col = col_ltr[label]
        wb.define_name(name,'='+sn+'!$'+col+'$'+str(start_row+1)+':$'+
            col+'$'+str(end_row+1))

    ws.autofilter(start_row-1,0, end_row, end_col)
    ws.freeze_panes(start_row,6)
    if debug:
        print('(now {} apps)'.format(len(df)))
        print('Done!',flush=True)
