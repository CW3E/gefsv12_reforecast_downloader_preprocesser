#!/usr/bin/env python3
"""
Preprocess GEFSv12 Reforecast Data
Author: Deanna Nash (dnash@ucsd.edu)

This script reads a YAML configuration and processes GEFSv12 reforecast data
for the specified variable and date.
"""

import sys
import yaml
from pathlib import Path
import xarray as xr
import pandas as pd
import numpy as np

sys.path.append('../modules')
import globalvars
import calc

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
config_file = sys.argv[1]
job_info = sys.argv[2]

with open(config_file, "r") as f:
    config = yaml.safe_load(f)

ddict = config[job_info]
required = ["year", "date", "varname"]
for k in required:
    if k not in ddict:
        raise KeyError(f"Missing '{k}' in config job '{job_info}'")

year = ddict["year"]
date = ddict["date"]
variable = ddict["varname"]

path_data = Path(globalvars.path_to_data)
path_downloads = path_data / "downloaded" / "GEFSv12_reforecast" / date
path_out = path_data / "preprocessed" / "GEFSv12_reforecast" / variable
path_out.mkdir(parents=True, exist_ok=True)

def process_variable_chunks(variable, date, year):
    """Handle 8-step chunks for ivt, uv, freezing_level."""
    chunk_datasets = []

    for start in range(0, 80, 8):
        stop = start + 8
        print(f"Processing {variable}: hours {start}-{stop}")

        if variable == "ivt":
            ds = calc.load_ivt_inputs(date, year, start, stop)

        elif variable == "uv":
            ds = calc.load_uv_inputs(date, year, start, stop, level=1000.)

        elif variable == "freezing_level":
            ds = calc.load_freezing_inputs(date, year, start, stop)

        else:
            raise ValueError(f"Unsupported variable: {variable}")

        ds = ds.isel(step=slice(0, 8)) # confirm that it only is 8 time steps

        # Name output file per chunk
        start_h = int(ds.step.values[0] / np.timedelta64(1, "h"))
        stop_h = int(ds.step.values[-1] / np.timedelta64(1, "h"))

        out_file = path_out / f"{date}_{variable}_F{start_h}_F{stop_h}.nc"
        print(f"Writing {out_file.name} ...")
        ds.load().to_netcdf(out_file, format="NETCDF4")

        chunk_datasets.append(ds)

    return chunk_datasets
    
# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if variable == "qpf":
    ds = process_qpf(date)
    out_file = path_out / f"{date}_qpf.nc"
    print(f"Writing {out_file.name}")
    ds.load().to_netcdf(out_file, format="NETCDF4")

else:
    process_variable_chunks(variable, date, year)
