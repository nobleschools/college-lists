#!python3
'''Master file for creating standard weekly reports either for a single
campus or all campuses in a list; can work from just naviance applications
file, but is designed to work with that plus a roster file (otherwise,
tries to get roster info from the Naviance file)'''

import yaml
import argparse
from reports_modules.output import Output
from reports_modules.excel_base import create_static_tabs, create_chart_tab
from reports_modules.create_summary import make_summary_tab
from reports_modules.create_students import reduce_roster, make_students_tab
from reports_modules.create_students import add_student_calculations
from reports_modules.create_apps import reduce_and_augment_apps, make_apps_tab
from reports_modules.create_single_student import make_single_tab

def main(settings_file, settings_tabs, campus, counselor, debug=True):
    '''Creates the reports according to instructions in yaml files either
    for a single campus or "All"'''
    # Setup configuration--main settings file (includes Excel formats)
    print('Report for {},{}.'.format(campus, counselor), flush=True)
    with open(settings_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    # Setup configuration--tab settings files (includes layout of tabs)
    cfg_tabs = {}
    for tab, filename in settings_tabs.items():
        with open(filename, 'r') as ymlfile:
            cfg_tabs[tab] = yaml.load(ymlfile)

    # Create the base output file
    out = Output(campus, counselor, cfg, cfg_tabs, debug)
    reduce_roster(campus, cfg, out.dfs, counselor,debug)
    reduce_and_augment_apps(cfg, out.dfs, debug)
    add_student_calculations(cfg, out.dfs, debug)

    create_chart_tab(out.writer, out.chart, debug)
    make_summary_tab(out.writer, out.formats, out.dfs, cfg,
            cfg_tabs['summary'], campus, debug)
    make_students_tab(out.writer, out.formats, out.dfs, cfg, 
            cfg_tabs['students'], campus, debug)
    make_single_tab(out.writer, out.formats, out.dfs, cfg,
            cfg_tabs['ssv'], campus, debug, blank=False)
    make_single_tab(out.writer, out.formats, out.dfs, cfg,
            cfg_tabs['ssv'], campus, debug, blank=True)
    make_apps_tab(out.writer, out.formats, out.dfs, cfg,
            cfg_tabs['applications'], debug)
    create_static_tabs(out.writer, out.dfs, out.formats, cfg, campus, debug)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate college app reports')

    parser.add_argument('-s','--settings',
            dest='settings_file', action='store',
            help='Name/path of yaml file with detailed settings',
            default='settings.yaml')

    parser.add_argument('-sm','--settings_summary',
            dest='settings_summary_file', action='store',
            help='Name/path of yaml file with summary settings',
            default='settings_summary.yaml')

    parser.add_argument('-ss','--settings_students',
            dest='settings_students_file', action='store',
            help='Name/path of yaml file with students settings',
            default='settings_students.yaml')

    parser.add_argument('-sa','--settings_applications',
            dest='settings_applications_file', action='store',
            help='Name/path of yaml file with students settings',
            default='settings_applications.yaml')

    parser.add_argument('-sv','--settings_ssv',
            dest='settings_ssv_file', action='store',
            help='Name/path of yaml file with single student report settings',
            default='settings_ssv.yaml')

    parser.add_argument('-ca', '--campus',
            dest='campus', action='store',
            help='Single campus name (default "All")',
            default='All')

    parser.add_argument('-co','--counselor',
            dest='counselor', action='store',
            help='Single counselor name (default "All")',
            default='All')

    parser.add_argument('-q','--quiet',
            dest='debug', action='store_false', default=True,
            help='Suppress status messages during report creation')

    args = parser.parse_args()
    settings_tabs = {
            'summary': args.settings_summary_file,
            'students': args.settings_students_file,
            'applications': args.settings_applications_file,
            'ssv': args.settings_ssv_file,
            }
    main(args.settings_file, settings_tabs, args.campus, args.counselor,
            args.debug)
