#!python3
'''Module for working with student records and making Students tab'''
from reports_modules.excel_base import safe_write, make_excel_indices

def reduce_roster(campus, cfg, dfs, counselor,debug):
    '''Uses campus info and config file to reduce the active student list'''
    df = dfs['full_roster']
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

def make_students_tab(writer, f_db, dfs, cfg, campus, debug):
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
    for stu_column in cfg['students_columns']:
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
                safe_write(ws, row, c, i,f_db[fmt])
            else:
                safe_write(ws, row, c, formula.replace('_r_',sr),f_db[fmt])
        row += 1

    # Add Names
    col_ltr = {x[1]:x[0] for x in master_cols}
    for name, label in cfg['student_names'].items():
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
