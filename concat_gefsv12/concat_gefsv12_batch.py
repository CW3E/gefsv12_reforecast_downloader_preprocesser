"""
Filename:    concat_gefsv12.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Concatenate GEFSv12 Reforecast data to daily netCDF files, and update metadata.
"""

import xarray as xr
import pandas as pd
import numpy as np
import os
import sys
import glob
sys.path.append('../modules')
import globalvars

path_to_data = globalvars.path_to_data
# -----------------------------
# Settings
# -----------------------------
START_DATE = "2000-01-01"
END_DATE   = "2019-12-31"
DAYS_PER_JOB = 10

varname = "uv" ## 'ivt', 'freezing_level', 'uv'

# -----------------------------
# Get SLURM task id
# -----------------------------
task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])

# -----------------------------
# Build date list
# -----------------------------
dates = pd.date_range(START_DATE, END_DATE, freq="D")

start_idx = task_id * DAYS_PER_JOB
end_idx   = start_idx + DAYS_PER_JOB

if start_idx >= len(dates):
    print("No dates assigned to this task.")
    sys.exit()

date_subset = dates[start_idx:end_idx]

print(f"Processing dates: {date_subset}")

# -----------------------------
# Loop over dates
# -----------------------------
for dt in date_subset:

    date = dt.strftime("%Y%m%d")

    out_name = os.path.join(
        path_to_data,
        f"preprocessed/GEFSv12_reforecast/{varname}_final/"
        f"GEFSv12_reforecast_{varname}_{date}.nc"
    )

    # -----------------------------
    # Restart-safe check
    # -----------------------------
    if os.path.exists(out_name):
        print(f"Skipping {date} (already processed)")
        continue

    # -----------------------------
    # Load all forecast step files
    # -----------------------------
    fname_pattern = os.path.join(
        path_to_data,
        f'preprocessed/GEFSv12_reforecast/{varname}/{date}_{varname}_F*.nc'
    )
    files = glob.glob(fname_pattern)

    if len(files) == 0:
        print(f"No files found for {date}, skipping")
        continue
        
    forecast = xr.open_mfdataset(
        fname_pattern,
        engine="netcdf4",
        concat_dim="step",
        combine="nested",
        decode_timedelta=True,
        coords="minimal",
        data_vars="minimal",
        compat="override",
        parallel=False
    )
    
    # Make sure forecast steps are sorted
    forecast = forecast.sortby("step")

    # calculate wind magnitude
    if varname == 'uv':
        forecast["uv"] = np.sqrt(forecast['u']**2 + forecast['v']**2)
    
    
    # -----------------------------
    # Update variable metadata
    # -----------------------------
    var_attrs = {
        "step": {"long_name": "time since init_time"},
        "ivt":  {"long_name": "integrated water vapor transport",
                 "units": "kg m-1 s-1"},
        "ivtu": {"long_name": "zonal integrated water vapor transport",
                 "units": "kg m-1 s-1"},
        "ivtv": {"long_name": "meridional integrated water vapor transport",
                 "units": "kg m-1 s-1"},
        "uv": {"long_name": "wind magnitude",
               "units": "m s-1"},
    }
    
    for var, attrs in var_attrs.items():
        if var in forecast:
            forecast[var].attrs.update(attrs)
    
    # Add some global attributes (optional)
    forecast.attrs.update({
        "description": f"GEFSv12 reforecast {varname} fields merged into a single file",
        "init_date": date,
    })
    
    
    # -----------------------------
    # Rename dimension (if present)
    # -----------------------------
    rename_dict = {}

    # rename coords if they exist
    if "time" not in forecast.coords:
        # fallback: create from metadata
        np_date = pd.to_datetime(
            forecast.attrs["init_date"],
            format="%Y%m%d"
        ).to_datetime64()
        forecast = forecast.assign_coords(time=np_date)
    
    # spatial renaming
    if "lat" in forecast.coords or "lat" in forecast.dims:
        rename_dict["lat"] = "latitude"
    
    if "lon" in forecast.coords or "lon" in forecast.dims:
        rename_dict["lon"] = "longitude"
    
    # apply renames once
    if rename_dict:
        forecast = forecast.rename(rename_dict)
    
    # -----------------------------
    # Drop unneeded variables
    # -----------------------------
    forecast = forecast.drop_vars("surface", errors="ignore")
    
    
    # -----------------------------
    # Save to NetCDF
    # -----------------------------
    
    def compression_dict(ds, zlib=True, complevel=5):
        return {
            var: {
                "zlib": zlib,
                "complevel": complevel,
                "dtype": "float32",
            }
            for var in ds.data_vars
        }
        
    ds_cleaned = forecast.drop_encoding()
    
    ds_cleaned.load().to_netcdf(out_name, mode='w', format='NETCDF4', encoding=compression_dict(ds_cleaned))
    print(f"Saved: {out_name}")