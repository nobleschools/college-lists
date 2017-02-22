#!python3
'''Main functional test suite for college-lists
   Currently expects to be called from main project directory'''

import os
import sys
import unittest
import pandas as pd

d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_names = ['Network Weekly Report NOBLE_TEST.xlsx',
              'Golder Weekly Report NOBLE_TEST.xlsx',
              'Jeffie Troxler Golder Weekly Report NOBLE_TEST.xlsx']
ref_names = ['tests/master_reference_file.xlsx',
             'tests/golder_reference_file.xlsx',
             'tests/troxler_reference_file.xlsx']
sheet_names = ['Students',
               'Applications',
               ]
call_stem = 'python "'+os.path.join(d,'create_reports.py')+'"'

def compare_excel_sheets(file1, file2, sheet_name):
    """Compares the contents of two excel sheets and returns whether
    any differences whatsoever"""
    df1 = pd.read_excel(file1, sheet=sheet_name)
    df2 = pd.read_excel(file2, sheet=sheet_name)
    df_diff = df1[df1!=df2]
    return bool(df_diff.any().any())

class NobleSetupTest(unittest.TestCase):
    def setUp(self):
        os.system(call_stem+
                ' -q -s tests/noble_settings.yaml')
        os.system(call_stem+
                ' -q -s tests/noble_settings.yaml -ca Golder')
        os.system(call_stem+
            ' -q -s tests/noble_settings.yaml -ca Golder -co "Jeffie Troxler"')
    def tearDown(self):
        for test_name in test_names:
            try:
                os.remove('tests/'+test_name)
            except:
                pass
            os.rename(test_name, 'tests/'+test_name)

    def test_tabs_match_the_example_file(self):
        for sheet in sheet_names:
            for i in range(len(test_names)):
                self.assertIs(compare_excel_sheets(test_names[i], 
                        ref_names[i], sheet), False)

        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
