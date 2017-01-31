# college-lists
**Code to automate creation of Excel based portfolio reports**

This project creates an Excel spreadsheet used by a high school to
aid in the counseling of seniors on their college lists.

##It has two data inputs:
- current_applications.csv: an applications file (formatted like a Naviance export)
- current_students.csv: a roster file (see further notes for specification)

##It has one "control" input:
- settings.yaml: master configuration file for the report

It has multiple global data inputs (in the 'inputs' folder):
- all_colleges.csv: general data about colleges, mostly from NCES data files
- college_list_lookup.csv: A translation from college name to NCES id
- custom_weights.csv: Empirical coefficients to calculate admissions odds
- standard_weights.csv: Empirical coefficients to calculate admissions odds
- strategy_definitions.csv: Definition of similar ranges of student selectivity
- targets_by_strategy.csv: Student goals for college institutional grad rate

-----
Using these inputs, the main script, 'create_reports.py' creates an Excel
report with a number of tabs. These replicate reports used by Noble that
were originally developed in Excel, but that can be customized to a certain
degree by changes to the yaml file.
