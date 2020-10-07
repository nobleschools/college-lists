#!python3
"""Master file for taking year-end college choices and a) creating an
Excel workbook for inspecting choices and b) creating a targets file
for use in the Bot and Weekly Reports"""

import yaml
import argparse
import pandas as pd
from reports_modules.output import Output
from reports_modules.excel_base import create_static_tabs, create_chart_tab
from reports_modules.create_students import reduce_roster, make_students_tab
from reports_modules.create_students import add_playbook_calculations


def make_summary_tab(writer, dfs):
    """Stop gap code to create summaries"""
    print("Writing summary tab...", flush=True, end="")
    df = dfs["roster"]
    sum_df = df[["local_bucket", "EFC"]].groupby(["local_bucket"]).count()
    sum_df.rename(columns={"EFC": "N"}, inplace=True)
    # Median
    sum_df = pd.concat(
        [
            sum_df,
            df[["local_bucket", "local_grad_rate"]]
            .groupby(["local_bucket"])
            .median()
            .rename(columns={"local_grad_rate": "median"}),
        ],
        axis=1,
    )
    # 75th percentile
    sum_df = pd.concat(
        [
            sum_df,
            df[["local_bucket", "local_grad_rate"]]
            .groupby(["local_bucket"])
            .quantile(0.75)
            .rename(columns={"local_grad_rate": "75th"}),
        ],
        axis=1,
    )

    sum_df.to_excel(writer, sheet_name="Summary", na_rep="N/A")
    df.to_excel(writer, sheet_name="Debug", na_rep="N/A")
    print("...Done!", flush=True)


def main(settings_file, settings_tabs, debug):
    '''Creates the reports according to instructions in yaml files either
    for a single campus or "All"'''
    # Setup configuration--main settings file (includes Excel formats)
    with open(settings_file, "r") as ymlfile:
        cfg = yaml.load(ymlfile)

    # Setup configuration--tab settings files (includes layout of tabs)
    cfg_tabs = {}
    for tab, filename in settings_tabs.items():
        with open(filename, "r") as ymlfile:
            cfg_tabs[tab] = yaml.load(ymlfile)

    # Create the base output file
    out = Output("All", "All", cfg, cfg_tabs, debug, False)
    reduce_roster("All", cfg, out.dfs, "All", debug)
    add_playbook_calculations(cfg, out.dfs, debug)

    create_chart_tab(out.writer, out.chart, debug)
    make_students_tab(
        out.writer, out.formats, out.dfs, cfg, cfg_tabs["students"], "All", debug
    )

    # This is a hack for now
    make_summary_tab(out.writer, out.dfs)

    create_static_tabs(
        out.writer, out.dfs, out.formats, cfg, "All", debug, playbook=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate playbook from end of year choices"
    )

    parser.add_argument(
        "-s",
        "--settings",
        dest="settings_file",
        action="store",
        help="Name/path of yaml file with detailed settings",
        default="settings/settings_playbook.yaml",
    )

    parser.add_argument(
        "-ss",
        "--settings_students",
        dest="settings_students_file",
        action="store",
        help="Name/path of yaml file with students settings",
        default="settings/settings_playbook_students.yaml",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        dest="debug",
        action="store_false",
        default=True,
        help="Suppress status messages during report creation",
    )

    args = parser.parse_args()
    settings_tabs = {
        "students": args.settings_students_file,
    }

    main(args.settings_file, settings_tabs, args.debug)
