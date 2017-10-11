#!python3
"""Runs tests for college-lists"""
from time import time
import os
import sys

if len(sys.argv) > 1:
    call_type = sys.argv[1]
else:
    call_type = 'counselor'

t0 = time()
# initially, just runs a basic counselor setup
call_stem = 'python create_reports.py -pdfonly'
call_counselor = '-co "Emily Morgan" -ca Muchin'
call_campus = '-ca RoweClark -sum Counselor'
if call_type == 'all':
    os.system(call_stem +' -sum Campus')
elif call_type == 'campus':
    os.system(call_stem+' '+call_campus)
else:
    os.system(call_stem+' '+call_counselor)
print('Total runtime of {} seconds'.format(time()-t0))
