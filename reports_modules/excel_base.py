#!python3
'''Functions to create the excel output'''
import string
import pandas as pd

def safe_write(ws, r, c, val, f=None, n_a=''):
    '''calls the write method of worksheet after first screening for NaN'''
    if not pd.isnull(val):
        if f:
            ws.write(r, c, val, f)
        else:
            ws.write(r, c, val)
    elif n_a:
        if f:
            ws.write(r, c, n_a, f)
        else:
            ws.write(r, c, n_a)

def write_array(ws, r, c, val, f=None):
    """speciality function to write an array. Assumed non-null"""
    if f:
        ws.write_formula(r, c, val, f)
    else:
        ws.write_formula(r, c, val)


def create_formats(wb, cfg_fmt, f_db={}):
    '''Takes a workbook and (likely empty) database to fill with formats'''
    for name, db in cfg_fmt.items():
        f_db[name] = wb.add_format(db)

    return f_db

def make_excel_indices():
    '''returns an array of Excel header columns from A through ZZ'''
    alphabet = string.ascii_uppercase
    master = list(alphabet)
    for i in range(len(alphabet)):
        master.extend([alphabet[i]+x for x in alphabet])
    return master

def _do_initial_output(writer, df, sheet_name,na_rep):
    '''Helper function to push data to xlsx and return formatting handles'''
    df.to_excel(writer, sheet_name=sheet_name, na_rep=na_rep)
    wb = writer.book
    ws = writer.sheets[sheet_name]
    max_row = len(df)+1
    return (wb, ws, sheet_name, max_row)
    
def create_targets_tab(writer, df, format_db):
    '''create the Targets tab from static file'''
    wb, ws, sn, max_row = _do_initial_output(writer, df, 'Targets', 'N/A')
    ws.set_column('B:G', 15, format_db['percent_fmt'])
    wb.define_name('TargetLookup','='+sn+'!$A$2:$G$'+str(max_row))
    ws.hide()

def create_strategies_tab(writer, df, format_db):
    '''Create Strategies tab from static file'''
    wb, ws, sn, max_row = _do_initial_output(writer, df, 'Strategies', 'N/A')
    wb.define_name('StrategyLookup','='+sn+'!$A$2:$D$'+str(max_row))
    ws.autofilter('A1:D1')
    ws.hide()

def create_standard_weights_tab(writer, df, format_db):
    '''Creates Coefficients tab from static file'''
    wb, ws, sn, max_row = _do_initial_output(writer, df, 'Coefficients', 'N/A')
    ws.set_column(0,0,30, format_db['left_normal_text'])

    names = {
            'Index':'A',
            'MatchCode':'B',
            'GPA':'C',
            'ACT':'D',
            'Intercept':'E',
            }
    for name, col in names.items():
        wb.define_name(sn+name,'='+sn+'!$'+col+'$2:$'+col+'$'+str(max_row))
    ws.autofilter('A1:E1')
    ws.hide()


def create_custom_weights_tab(writer, df, format_db):
    '''Creats CustomWeights tab from static file'''
    wb, ws, sn, max_row = _do_initial_output(writer, df, 'CustomWeights', '')
    ws.set_column(5,5,100, format_db['left_normal_text'])

    names = {
            'Index':'A',
            'GPA':'B',
            'ACT':'C',
            'Intercept':'D',
            }
    for name, col in names.items():
        wb.define_name(sn+name,'='+sn+'!$'+col+'$2:$'+col+'$'+str(max_row))
    ws.autofilter('A1:F1')
    ws.hide()
                

def create_college_list_lookup_tab(writer, df, format_db):
    '''Creates CollegeListLookup tab from static file'''
    wb, ws, sn, max_row = _do_initial_output(writer,df,'CollegeListLookup','')
    ws.set_column(0,0,40, format_db['left_normal_text'])
    wb.define_name('ExtraCollegeChoice',
            '='+sn+'!$A$2:$A$'+str(max_row))
    wb.define_name('ExtraCollegeNCES',
            '='+sn+'!$B$2:$B$'+str(max_row))
    wb.define_name('CollegeListLookup',
            '='+sn+'!$A$2:$B$'+str(max_row))
    ws.autofilter('A1:C1')
    ws.hide()
    
def create_all_colleges_tab(writer, df, format_db):
    '''Creates AllColleges from static file'''
    wb, ws, sn, max_row = _do_initial_output(writer,df,'AllColleges','N/A')

    ws.set_column('D:E', 7, format_db['percent_fmt'])
    ws.set_column('B:B', 40)
    ws.set_column('C:C', 22)
    ws.set_column('F:L', 7)
    names = {
            'NCES':'A',
            'Names':'B',
            'Barrons':'C',
            'GR':'D',
            'AAHGR': 'E',
            'ACT25': 'F',
            'ACT50': 'G',
            'MoneyCode':'H',
            'Money':'I',
            'HBCU':'J',
            'ILPub':'K',
            'Chicago':'L',
            }
    for name, col in names.items():
        wb.define_name(sn[:-1]+name,'='+sn+'!$'+col+'$2:$'+col+'$'+str(max_row))

    max_col = max(names.values())
    wb.define_name(sn[:-1]+'Lookup',
            '='+sn+'!$A$2:$'+max_col+'$'+str(len(df)+1))
    ws.autofilter('A1:'+max_col+'1')
    ws.hide()

def create_labels_tab(writer, format_db, cfg, campus):
    '''Create static labels tab based on config file input'''
    wb = writer.book
    sn = 'Labels'
    ws = wb.add_worksheet(sn)
    ws.write(0,0, 'Label Reference', format_db['bold'])
    ws.write(0,1, 'Label Value', format_db['bold'])
    ws.write(0,2, 'Short Value', format_db['bold'])
    source = cfg['category_labels']
    if campus in source: # there is a special set of labels for this campus
        source = source[campus]
    else:
        source = source['Standard']

    current_row = 1
    for k, v in source.items():
        ws.write(current_row,0,k+'Label')
        ws.write(current_row,1,v)
        wb.define_name(k+'Label', sn+'!$B$'+str(current_row+1))
        if k == 'TargetGR':
            ws.write(current_row,2,'=LEFT(TargetGRLabel,1)&"GR"')
            wb.define_name('TGRshortLabel',sn+'!$C$'+str(current_row+1))
        elif k == 'IdealGR':
            ws.write(current_row,2,'=LEFT(IdealGRLabel,1)&"GR"')
            wb.define_name('IGRshortLabel',sn+'!$C$'+str(current_row+1))
        current_row += 1

    ws.set_column(0,1,18)
    ws.hide()

def create_static_tabs(writer, dfs, formats, cfg, campus,debug):
    '''Places default data into hidden tabs'''
    if debug:
        print('Writing static tabs...',flush=True,end='')
    static_tabs_from_csv = [
            (create_all_colleges_tab,'AllColleges'),
            (create_college_list_lookup_tab,'CollegeListLookup'),
            (create_custom_weights_tab,'CustomWeights'),
            (create_standard_weights_tab,'StandardWeights'),
            (create_strategies_tab,'Strategies'),
            (create_targets_tab,'StudentTargets'),
            ]
    for runner, tab_name in static_tabs_from_csv:
        runner(writer, dfs[tab_name], formats)

    create_labels_tab(writer, formats, cfg, campus)

    if debug:
        print('Done!', flush=True)
