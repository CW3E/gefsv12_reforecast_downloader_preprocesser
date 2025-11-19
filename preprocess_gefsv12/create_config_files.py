######################################################################
# Filename:    create_job_configs.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create .yaml configuration file to run job_array with slurm for downloading GEFSv12 Reforecast Data
#
######################################################################
import os, sys
import pandas as pd
import yaml
from itertools import chain

sys.path.append('../modules')
import globalvars

# adjustable maximum jobs per config file
MAX_JOBS_PER_FILE = 999
conda_path = globalvars.conda_path
varnames = ["ivt", "freezing_level", "uv", "qpf"]

for varname in varnames:
    # create list of daily dates
    start_date = pd.to_datetime(f"2000-01-01")
    end_date = pd.to_datetime(f"2019-12-31")
    date_lst = pd.date_range(start_date, end_date, freq="1D")

    jobcounter = 0
    filecounter = 0
    d_lst = []
    njob_lst = []

    # loop through dates to build config entries
    for date in date_lst:
        yr = date.strftime("%Y")

        jobcounter += 1
        d = {
            f"job_{jobcounter}": {
                "year": yr,
                "date": date.strftime("%Y%m%d"),
                "varname": varname,
            }
        }
        d_lst.append(d)

        # write to YAML once we reach MAX_JOBS_PER_FILE
        if jobcounter == MAX_JOBS_PER_FILE:
            filecounter += 1
            dest = dict(chain.from_iterable(map(dict.items, d_lst)))
            njob_lst.append(len(d_lst))
            with open(f"config_{varname}_{filecounter}.yaml", "w") as file:
                yaml.dump(dest, file, allow_unicode=True, default_flow_style=None)

            # reset for next file
            jobcounter = 0
            d_lst = []

    # write remaining jobs if any left
    if d_lst:
        filecounter += 1
        dest = dict(chain.from_iterable(map(dict.items, d_lst)))
        njob_lst.append(len(d_lst))
        with open(f"config_{varname}_{filecounter}.yaml", "w") as file:
            yaml.dump(dest, file, allow_unicode=True, default_flow_style=None)

    # now create calls_VARNAME_N.txt for each config file
    for i, njobs in enumerate(njob_lst):
        call_str_lst = []
        for j in range(1, njobs + 1):
            call_string = f"{conda_path} -u preprocess_GEFSv12_reforecast.py config_{varname}_{i+1}.yaml 'job_{j}'"
            call_str_lst.append(call_string)

        with open(f"calls_{varname}_{i+1}.txt", "w", encoding="utf-8") as f:
            for line in call_str_lst:
                f.write(line + "\n")
