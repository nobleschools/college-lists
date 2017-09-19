#!python3
'''Module for working with student records and making Students tab'''
from reports_modules.excel_base import safe_write, write_array
from reports_modules.excel_base import make_excel_indices

def parse_formulas(formula, col_ltr, sum_name):
    '''parses formula strings and replaces references to other columns
    or the specially summary field
    col_ltr is a dict of Excel names for each column
    sum_name is the name of the summary field'''
    # First look to replace the pattern %this% with letter_r_
    tokens = formula.split('%')
    # look at every other token "=formula(%this%,%that%)", we want this, that
    for i in range(1,len(tokens),2): 
        if tokens[i] == '*': # this is the special signal that we'll sub a range
            tokens[i] = sum_name
        else:
            tokens[i] = col_ltr[tokens[i]]+'_r_'
    new_formula = ''.join(tokens)

    # Second replace the pattern |this| with letter_sr_:letter_er_
    tokens = new_formula.split('|')
    # Same logic as the prior loop
    for i in range(1, len(tokens), 2):
        letter = col_ltr[tokens[i]]
        tokens[i] = letter+'_sr_:'+letter+'_er_'
    new_formula = ''.join(tokens)

    # Finally, replace the pattern @this@ with letter_xr_
    tokens = new_formula.split('@')
    for i in range(1, len(tokens), 2):
        letter = col_ltr[tokens[i]]
        tokens[i] = letter+'_xr_'
    return ''.join(tokens)

def push_column(columns, letters, label, formula, fmt,
                width, label_fmt, cond_format, sum_formula,
                sum_format, sum_name):
    '''Adds a list of length 9 to the master column list with
    col0=Excel header, col1=label, col2=formula; replaces %label% with
    the corresponding letter in Excel for that letter plus a _r_ and
    replaces #label# with letter_sr_:letter_er_,
    col3=format (data), col4=width,
    col5=label format, col6=conditional format
    col7=summary format, col8=summary format
    Inputs:
    columns = list of existing columns (each element list of length 7)
    letters = reference list of each column header in Excel
    label = the label in Excel for the new column
    formula = the formula field for the new column
    fmt = the format label for the new column
    width = width of the new column
    label_fmt = the format label for the header of the new column
    cond_format = conditional format to add if at a marked off row
    sum_formula = a second formula field for the final row
    sum_format = a third format field for the final row
    sum_name = the name to use if the %*% pattern is encountered'''
    # Here, col_ltr is assigned a local database of the Excel reference for
    # each column already in the master 'columns' list
    col_ltr = {x[1]:x[0] for x in columns}

    # Assigns the new column to the next Excel reference and tacks on the label
    col_ltr[label] = letters[len(columns)] # so we can reference this column
    new_col = [letters[len(columns)],label]
    
    # now add [2], the formula after parsing and replacing references
    new_col.append(parse_formulas(formula, col_ltr, sum_name))
    new_col.extend([fmt, width, label_fmt, cond_format]) #3-6
    new_col.append(parse_formulas(sum_formula, col_ltr, sum_name))
    new_col.append(sum_format)
    columns.append(new_col)
    return columns

def make_summary_tab(writer, f_db, dfs, cfg, cfg_sum, campus, debug):
    '''Creates the Excel tab for students using cfg details'''
    # First initialize inputs
    if debug:
        print('Writing summary tab...',flush=True,end='')
    df = dfs['roster']
    wb = writer.book
    sn = 'Summary'
    ws = wb.add_worksheet(sn)
    master_cols = []
    col_letters = make_excel_indices() # creates an index of excel headers
    # the summary_type field selects the right set of field details
    summary_fields = cfg_sum['summary_fields']
    summary_field = summary_fields[cfg['summary_type']]
    sum_name = summary_field['excel_name'] #named range in Students
    sum_label = summary_field['excel_label'] #how we should label this field
    sum_local = summary_field['tbl_name'] #field in roster table to sum by
    rows = list(set(df[sum_local])) # A list of unique values in sum column

    # Now define a list of columns and how they are constructed
    for sum_column in cfg_sum['summary_columns']:
        for column_name in sum_column: # there's only one, but need to deref
            col = sum_column[column_name]
            if col['formula'].startswith('cfg:'):
                cfg_ref = col['formula'][4:]
                if campus in cfg[cfg_ref]:
                    formula = cfg[cfg_ref][campus]
                else:
                    formula = cfg[cfg_ref]['Standard']
            else:
                formula = col['formula']

            # Process the information for this column and push to a list
            # of columns ready to write out
            master_cols = push_column(master_cols, col_letters, column_name,
                    formula, col['format'], col['width'],
                    col['label_format'], col['cond_format'], 
                    col['sum_formula'], col['sum_format'], sum_name)
    
    # After everything is defined, overwrite the label to the first column:
    master_cols[0][1] = sum_label

    # Now write the column headers:
    for i in range(len(master_cols)):
        col = master_cols[i]
        safe_write(ws,0,i,col[1],f_db[col[5]])

    # Setup the data columns
    start_row = 1
    end_row = len(rows)
    end_col = len(master_cols)-1

    # Do the data columns:
    row = start_row
    for i in range(len(rows)):
        sr = str(row+1)
        for c in range(len(master_cols)):
            letter, label, formula, fmt = master_cols[c][:4]
            new_formula = formula.replace('_r_', sr).replace(
                '_sr_', str(start_row+1)).replace(
                '_er_', str(end_row+1)).replace('_xr_', str(end_row+2))
            if formula == 'tbl:sum_field':
                safe_write(ws, row, c, rows[i],f_db[fmt])
            elif formula.startswith('<id>'):
                safe_write(ws, row, c, i, f_db[fmt])
            elif formula.startswith('{'):
                write_array(ws, row, c, new_formula, f_db[fmt])
            else:
                safe_write(ws, row, c, new_formula, f_db[fmt])
        row += 1

    # Do summary row
    sr = str(row+1)
    for c in range(len(master_cols)):
        sum_formula, sum_fmt = master_cols[c][-2:]
        new_formula = sum_formula.replace('_r_', sr).replace(
                '_sr_', str(start_row+1)).replace(
                '_er_', str(end_row+1)).replace('_xr_', str(end_row+2))
        safe_write(ws, row, c, new_formula, f_db[sum_fmt])

    # Do the conditional formating underlines
    for i in range(len(master_cols)):
        ws.conditional_format(start_row, i, end_row, i,
            {'type':'formula',
             'criteria': '=IF(MOD(ROW()-1,4)=0,TRUE,FALSE)',
             'format':f_db[master_cols[i][6]]})

    # Set widths:
    for i in range(len(master_cols)):
        width = master_cols[i][4]
        if isinstance(width, str): # an 'h' was appended to the width
            ws.set_column(i,i,float(width[:-1]),f_db['centered'],
                    {'hidden':True})
        else:
            ws.set_column(i,i,width)
    
    # Finally, the rest of the tab's formatting
    ws.set_row(0,45)
    #ws.freeze_panes(start_row,2)
    if debug:
        print('Done!',flush=True)
