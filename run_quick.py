#!python3
"""Runs tests for college-lists"""
from time import time
import os

t0 = time()
# initially, just runs a basic counselor setup
call_stem = 'python create_reports.py'
call_counselor = '-co "Emily Morgan" -ca Muchin'
os.system(call_stem+' '+call_counselor)
print('Total runtime of {} seconds'.format(time()-t0))
