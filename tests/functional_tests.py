#!python3
'''Main functional test suite for college-lists
   Currently expects to be called from main project directory'''

import os
import sys
import unittest

d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
call_stem = 'python "'+os.path.join(d,'create_reports.py')+'"'

class NobleSetupTest(unittest.TestCase):
    def setUp(self):
        os.system(call_stem+
                ' -s tests/noble_settings.yaml')
    def tearDown(self):
        pass
        # Eventually, we'd delete the tested file here

    def test_students_tab_matches_the_example_file(self):
        # We'll use pandas to compare the content of the two files
        self.fail('Finish the test!')

    '''
    def test_applications_tab_matches_the_example_file(self):
        # We'll use pandas to compare the content of the two files
        self.fail('Finish the test!')
    '''

if __name__ == '__main__':
    unittest.main(warnings='ignore')
