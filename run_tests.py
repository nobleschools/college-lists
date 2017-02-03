#!python3
"""Runs tests for college-lists"""

import os
# initially, just runs a basic counselor setup
call_stem = 'python create_reports.py'
call_counselor = '-co "Emily Morgan" -ca Muchin'
os.system(call_stem+' '+call_counselor)
