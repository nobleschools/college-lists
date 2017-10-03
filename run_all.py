#!python3
"""Runs all college-lists"""
from time import time
#import datetime
import os

#dtfolder = datetime.datetime.now().strftime('%m_%d_%Y')
#os.mkdir(dtfolder)
call_stem = 'python create_reports.py'
'''
t0 = time()
os.system(call_stem+' -sum Campus')
print('Network: {:.2f} seconds'.format(time()-t0),flush=True)
'''

for campus_case in [
        'Noble',
        'Pritzker',
        'Rauner',
        'Golder',
        'RoweClark',
        'Comer',
        'UIC',
        'Bulls',
        'Muchin',
        'Johnson',
        'DRW',
        'Hansberry',
        'Baker',
        'Butler',
        'Speer',
        'TNA',
        ]:
    t0 = time()
    print('Generating {}...'.format(campus_case),flush=True,end='')
    os.system(call_stem+' -q -ca '+campus_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)

'''
for c_case in [
        '"Caroline Ryden"',
        '"Jane Knoche"',
        '"Laura Edwards"',
        '"Mark Williams"',
        '"Sarah Kruger"',
        ]:
    t0 = time()
    print('Generating {}...'.format('Pritzker;'+c_case),flush=True,end='')
    os.system(call_stem+' -q -ca Pritzker -co '+c_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)

for c_case in [
        '"Edith Flores"',
        '"Julie Horning"',
        '"Lauren Chelew"',
        ]:
    t0 = time()
    print('Generating {}...'.format('Golder;'+c_case),flush=True,end='')
    os.system(call_stem+' -q -ca Golder -co '+c_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)

for c_case in [
        'Bermudez',
        'Boros',
        'Paiz',
        'Weingartner',
        'Wilson',
        ]:
    t0 = time()
    print('Generating {}...'.format('TNA;'+c_case),flush=True,end='')
    os.system(call_stem+' -q -ca TNA -co '+c_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)

for c_case in [
        'Ballard',
        'Bowdy',
        'Desgrosellier',
        'MacCallum',
        ]:
    t0 = time()
    print('Generating {}...'.format('UIC;'+c_case),flush=True,end='')
    os.system(call_stem+' -q -ca UIC -co '+c_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)

'''
