#!python3
"""Runs all college-lists"""
from time import time
import datetime
import os
import zipfile

def compress(filefolder):
    '''Will replace a folder with a zip file of the same name
       NOTE: will only work with a flat directory--does not nest'''
    zipfn = os.path.basename(filefolder) + '.zip'
    with zipfile.ZipFile(zipfn, 'w', zipfile.ZIP_DEFLATED) as myzip:
        os.chdir(filefolder)
        for file in os.listdir('.'):
            print('Compressing %s.' % file)
            myzip.write(file)
            os.remove(file)
    os.chdir('..')
    os.rmdir(filefolder)

call_stem = 'python create_reports.py'

t0 = time()
os.system(call_stem+' -sum Campus')
print('Network: {:.2f} seconds'.format(time()-t0),flush=True)

# First do campus/counselor summary files
for campus_case in [
        'Butler',
        'Bulls',
        ]:
    t0 = time()
    before_files = os.listdir()
    print("Generating {} (don't add to directory)...".format(campus_case),
            flush=True,end='')
    os.system(call_stem+' -q -sum Counselor -ca '+campus_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)
    after_files = os.listdir()
    new_files = list(set(after_files)-set(before_files))
    new_file = new_files[0]
    os.rename(new_file, 'Counselor Summary '+new_file)

# Now do campus reports
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
        'PAS',
        'listKIPP.csv',
        'listGCMS.csv',
        ]:
    t0 = time()
    print('Generating {}...'.format(campus_case),flush=True,end='')
    if campus_case == 'Johnson':
        os.system(call_stem+' -s settings/settings_aa_only.yaml -q -ca '+campus_case)
    elif campus_case == 'listKIPP.csv' or campus_case == 'listGCMS.csv':
        os.system(call_stem+' -q -pdf -ca '+campus_case)
    else:
        os.system(call_stem+' -q -ca '+campus_case)
    print('{:.2f} seconds'.format(time()-t0),flush=True)

# Now do counselor specific cases for a handful of campuses
for campus, names in [
        ['Pritzker',['"Caroline Ryden"', '"Jane Knoche"',
         '"Laura Edwards"', '"Mark Williams"', '"Sarah Kruger"']],
        ['Golder',['"Edith Flores"','"Julie Horning"','"Lauren Chelew"']],
        ['Muchin',['"Paul Farrand"','"Emily Morgan"','"Emmanuel Jackson"',
            '"Dominique Vega"']],
        ['TNA',['Bermudez','Boros','Paiz','Weingartner','Wilson']],
        ['UIC',['Ballard','Bowdy','Desgrosellier','MacCallum']],
        ]:
    this_dir_before = os.listdir('.')
    for name in names:
        t0 = time()
        print('Generating {}...'.format(campus+';'+name),flush=True,end='')
        os.system(call_stem+' -q -ca '+campus+' -co '+name)
        print('{:.2f} seconds'.format(time()-t0),flush=True)
    this_dir_after = os.listdir('.')
    new_files = [x for x in this_dir_after if x not in this_dir_before]
    print(new_files)
    folder = datetime.datetime.now().strftime(campus+
            '_Counselor_Reports_%m_%d_%Y')
    os.mkdir(folder)
    for x in new_files:
        os.rename(x, folder+'/'+x)
    compress(folder)
