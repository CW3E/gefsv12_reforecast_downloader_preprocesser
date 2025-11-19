"""
Filename:    create_calls.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Create a text file that has the calls to concat
             GEFSv12 data to daily using SLURM array jobs,
             splitting into files with at most 999 jobs.
"""

from datetime import date, timedelta
from itertools import chain
import yaml
import pandas as pd

# ------------------------------
# Settings
# ------------------------------
start = date(2000, 1, 1)
end   = date(2019, 12, 31)

date_lst = pd.date_range(start, end, freq="1D")

MAX_JOBS_PER_FILE = 999
conda_path = "/home/dnash/miniconda3/envs/SEAK-impacts/bin/python"

# ------------------------------
# Build YAML config files
# ------------------------------
jobcounter = 0
filecounter = 0
d_lst = []
njob_lst = []

for dt in date_lst:
    jobcounter += 1

    # Store date as YYYYMMDD for consistency
    d = {f"job_{jobcounter}": {"date": dt.strftime("%Y%m%d")}}
    d_lst.append(d)

    # Write config file once we hit max chunk size
    if jobcounter == MAX_JOBS_PER_FILE:
        filecounter += 1
        dest = dict(chain.from_iterable(map(dict.items, d_lst)))
        njob_lst.append(len(d_lst))

        with open(f"config_{filecounter}.yaml", "w") as file:
            yaml.dump(dest, file, allow_unicode=True)

        # Reset counters
        jobcounter = 0
        d_lst = []

# Write remainder
if d_lst:
    filecounter += 1
    dest = dict(chain.from_iterable(map(dict.items, d_lst)))
    njob_lst.append(len(d_lst))

    with open(f"config_{filecounter}.yaml", "w") as file:
        yaml.dump(dest, file, allow_unicode=True)

# ------------------------------
# Create calls_*.txt files
# ------------------------------
for i, njobs in enumerate(njob_lst):
    call_str_lst = []

    for j in range(1, njobs + 1):
        call_str = f"{conda_path} -u concat_gefsv12.py config_{i+1}.yaml 'job_{j}'"
        call_str_lst.append(call_str)

    with open(f"calls_{i+1}.txt", "w", encoding="utf-8") as f:
        for line in call_str_lst:
            f.write(line + "\n")
