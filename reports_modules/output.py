#!python3
'''Container class for storing output and related tables'''

from datetime import datetime
import pandas as pd

from reports_modules.excel_base import create_formats

def safe2int(x):
    '''converts to int if possible, otherwise is a string'''
    try:
        return int(x)
    except:
        return x

def safe2f(x):
    '''converts to float if possible, otherwise is a string'''
    try:
        return float(x)
    except:
        return x

def p2f(x):
    '''converts percent string to float number'''
    return None if x == 'N/A' else float(x.strip('%'))/100

class Output():
    '''Class to store core data and other Pandas tables along with references
    to the Excel output'''

    def _get_filename(self, campus, counselor, root, date_string):
        '''Returns the filename for this Excel object'''
        cmp = 'Network' if campus == 'All' else campus
        cmp = cmp+' '+root+' '+datetime.now().strftime(date_string)+'.xlsx'
        if counselor != 'All':
            cmp = counselor + ' ' + cmp
        return cmp

    def _read_inputs(self, key, filename):
        '''Handles the reading of input csv files with some special indices'''
        if self.debug:
            print('Importing {}: {}'.format(key,filename), flush=True,end='')
        if key == 'AllColleges':
            self.dfs[key] = pd.read_csv(filename,index_col=0,encoding='cp1252',
                    na_values='N/A',converters={
                        'UNITID':safe2int,
                        'Adj6yrGrad_All':p2f,
                        'Adj6yrGrad_AA_Hisp':p2f})
            if self.debug:
                print('(size {}).'.format(len(self.dfs[key])),flush=True)
        elif key == 'chart':
            self.chart = filename
        elif key == 'CollegeListLookup':
            self.dfs[key] = pd.read_csv(filename,index_col=0,encoding='cp1252',
                    converters={'UNITID':safe2int})
            if self.debug:
                print('(size {}).'.format(len(self.dfs[key])),flush=True)
        elif key in ['CustomWeights','StandardWeights','Strategies',
                     'StudentTargets','SATtoACT']:
            self.dfs[key] = pd.read_csv(filename,index_col=0,
                    na_values=['N/A',''])
            if self.debug:
                print('(size {}).'.format(len(self.dfs[key])),flush=True)
        elif key == 'current_roster':
            self.dfs['full_roster'] = pd.read_csv(filename,index_col=4,
                na_values=['N/A',''],encoding='cp1252',converters={
                    'EFC':safe2int,
                    'ACT':safe2int,
                    'SAT':safe2int,
                    'GPA':safe2f,
                    'StudentID':safe2int})
            if self.debug:
                print('(size {}).'.format(len(self.dfs['full_roster'])),
                        flush=True)
        elif key == 'current_applications':
            self.dfs['applications'] = pd.read_csv(filename,na_values=[''],
                    encoding='cp1252',
                    usecols=self.cfg_tabs['applications']['app_fields'],
                    converters={'NCES':safe2int})
            if self.debug:
                print('(size {}).'.format(len(self.dfs['applications'])),
                        flush=True)
        else:
            # only main input currently missing is current_applications
            if self.debug:
                print(' (not actually read)',flush=True)

    def __init__(self, campus, counselor, cfg, cfg_tabs, debug=False):
        '''Instantiates object based on an expected yaml file'''
        self.debug=debug
        self.cfg = cfg
        self.cfg_tabs = cfg_tabs
        self.fn = self._get_filename(campus, counselor,
                cfg['output_file']['root_name'],
                cfg['output_file']['date_format'])
        if self.debug:
            print('Filename will be ({}).'.format(self.fn))

        self.dfs = {} # place to hold all dataframes

        for k, v in cfg['inputs'].items():
            self._read_inputs(k,v)

        self.writer = pd.ExcelWriter(self.fn, engine='xlsxwriter')
        self.wb = self.writer.book
        self.formats = create_formats(self.wb, cfg['excel_formats'])

    def __del__(self):
        try:
            self.writer.save()
        except:
            pass
