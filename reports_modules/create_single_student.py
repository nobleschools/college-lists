#!python3
'''Module for working with single student reports'''
from reports_modules.excel_base import safe_write

def make_single_tab(writer, f_db, dfs, cfg, cfg_ssv, campus, debug, blank=True):
    '''Creates the Excel tab for single student report using cfg details
    If blank, then doesn't use the applications from that table'''
    '''As a whole, this tab is the most prescriptive about spacing and content
    At some point there may be more opportunity to customize via yaml file'''

    # First initialize inputs
    if debug:
        out_str = '(blank) ' if blank else ''
        print('Writing single student '+out_str+'tab...',flush=True,end='')
    #df = dfs['roster']
    wb = writer.book
    sn = 'SingleStudentView' + ('Blank' if blank else '')
    ws = wb.add_worksheet(sn)
    out_num = 0.97 if blank else 0.5
    safe_write(ws, 1, 1, out_num, f_db['ssv_percent'])
    
    # Finally, the rest of the tab's formatting
    ws.set_row(0,19.5)
    ws.set_column(0,3,8.0,f_db['ssv_yellow'],{'hidden':True})

    if not blank:
        ws.freeze_panes(13,0)

    if debug:
        print('Done!',flush=True)
        print(str(cfg_ssv))
