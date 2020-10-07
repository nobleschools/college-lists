#!python3
"""Runs just the basic college lists"""
from time import time
import os

call_stem = "python create_reports.py"

t0 = time()
os.system(call_stem + " -sum Campus")
print("Network: {:.2f} seconds".format(time() - t0), flush=True)

# Now do campus reports
for campus_case in [
    "Noble",
    "Pritzker",
    "Rauner",
    "Golder",
    "RoweClark",
    "Comer",
    "UIC",
    "Bulls",
    "Muchin",
    "Johnson",
    "DRW",
    "Hansberry",
    "Baker",
    "Butler",
    "Speer",
    "TNA",
    "PAS",
]:
    t0 = time()
    print("Generating {}...".format(campus_case), flush=True, end="")
    os.system(call_stem + " -q -pdf -ca " + campus_case)
    print("{:.2f} seconds".format(time() - t0), flush=True)
