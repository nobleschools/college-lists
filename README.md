# college-lists
**Code to automate creation of Excel based portfolio reports**

This project creates an Excel spreadsheet used by a high school to
aid in the counseling of seniors on their college lists.

In addition to the master Excel sheet with multiple tabs, it can
also produce a PDF report with one page per student, analyzing
their [current college lists](./ssv_example.pdf).

To preview the main output files, check out the 6 "reference" files (3 pdf &
3 Excel) in the tests folder. The "Network" files show the reports for a
system of schools, the "Beta HS" ones for a single school, and the "Jeffie
Troxler" files for a single counselor at that school.

---
## It has two data inputs:
- current_applications.csv: an applications file (formatted like a Naviance export)
- current_students.csv: a roster file (see further notes for specification)

## It has "control" inputs:
- settings.yaml: master configuration file for the report
- settings_applications.yaml: formatting for the applications tab
- settings_students.yaml: formatting for the students tab
- settings_summary.yaml: formatting for the summary tab
- settings_ssv.yaml: formatting for the single student reports (Excel and PDF)

## It has multiple global data inputs (in the 'inputs' folder):
- act_to_sat.csv: conversion chart from one to the other
- all_colleges.csv: general data about colleges, mostly from NCES data files
- college_list_lookup.csv: A translation from college name to NCES id for
  drop downs
- custom_weights.csv: Empirical coefficients to calculate admissions odds
- sat_to_act.csv: conversion chart from one to the other
- standard_weights.csv: Empirical coefficients to calculate admissions odds
- strategy_chart.jpg: Graphical representation of strategy_definitions.csv
- strategy_definitions.csv: Definition of similar ranges of student selectivity
- targets_by_strategy.csv: Student goals for college institutional grad rate

-----
Using these inputs, the main script, 'create_reports.py' creates an Excel
report with a number of tabs. These replicate reports used by Noble that
were originally developed in Excel, but that can be customized to a certain
degree by changes to the yaml file.

In addition to the Excel report, the "-pdf" or "-pdfonly" flag can be used
to create a multi-page pdf output with one sheet per student.
-----
## Examples of command line execution with various options:
- **Standard report with all students:**
    - python create_reports.py
- **Standard report with all students, quieting output**
    - python create_reports.py -q
    - python create_reports.py --quiet
- **Standard report with for a single campus**
    - python create_reports.py -ca Bulls
    - python create_reports.py --campus Bulls
- **Standard report with for a single campus and single counselor**
    - python create_reports.py -ca Bulls -co "Mary Counselor"
    - python create_reports.py --campus Bulls --counselor "Mary Counselor"
- **PDF report for a single campus**
	- python create_reports.py -ca Bulls -pdfonly # no Excel created
	- python create_reports.py -ca Bulls -pdf     # Excel and PDF created
