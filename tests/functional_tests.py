#!python3
'''Main functional test suite for college-lists
   Currently expects to be called from main project directory'''

import os
import sys
import unittest
import pandas as pd

d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_names = ['Network Weekly Report TEST.xlsx',
              'Beta HS Weekly Report TEST.xlsx',
              'Jeffie Troxler Beta HS Weekly Report TEST.xlsx',
              'Network Weekly Report TEST SSV.pdf',
              'Beta HS Weekly Report TEST SSV.pdf',
              'Jeffie Troxler Beta HS Weekly Report TEST SSV.pdf']
ref_names = ['tests/master_reference_file.xlsx',
             'tests/beta_reference_file.xlsx',
             'tests/troxler_reference_file.xlsx',
             'tests/master_reference_file_ssv.pdf',
             'tests/beta_reference_file_ssv.pdf',
             'tests/troxler_reference_file_ssv.pdf',]
sheet_names = [
               'Summary',
               'Students',
               'SingleStudentView',
               'SingleStudentViewBlank',
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

def compare_pdf_files(file1, file2):
    """
    Compares two PDF files; current just looks at size
    """
    return os.path.getsize(file1) == os.path.getsize(file2)

class ListsSetupTest(unittest.TestCase):
    def setUp(self):
        base_settings = ' -q -pdf -s tests/test_settings.yaml -sv tests/test_settings_ssv.yaml'
        os.system(call_stem+base_settings)
        os.system(call_stem+base_settings+' -ca "Beta HS"')
        os.system(call_stem+base_settings+' -ca "Beta HS" -co "Jeffie Troxler"')
    def tearDown(self):
        for test_name in test_names:
            try:
                os.remove('tests/'+test_name)
            except:
                pass
            os.rename(test_name, 'tests/'+test_name)

    def test_tabs_match_the_example_file(self):
        for i in range(len(test_names)):
            if ref_names[i].endswith('.pdf'):
                self.assertTrue(compare_pdf_files(test_names[i],ref_names[i]))
            else:
                for sheet in sheet_names:
                    self.assertFalse(compare_excel_sheets(test_names[i], 
                        ref_names[i], sheet))

        #self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
