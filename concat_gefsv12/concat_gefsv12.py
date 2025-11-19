"""
Filename:    concat_gefsv12_ivt.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Concatenate GEFSv12 Reforecast data to daily netCDF files, and update metadata.
"""

import xarray as xr
import os
import sys
import yaml
sys.path.append('../modules')
import globalvars

path_to_data = globalvars.path_to_data

### Imports config name from argument when submit
yaml_doc = sys.argv[1]
config_name = sys.argv[2]

# import configuration file for dictionary choice
config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
ddict = config[config_name]

date = ddict['date']

varname = 'ivt'

# -----------------------------
# Load all forecast step files
# -----------------------------
fname_pattern = os.path.join(
    path_to_data,
    f'preprocessed/GEFSv12_reforecast/{varname}/{date}_{varname}_F*.nc'
)
print(fname_pattern)
forecast = xr.open_mfdataset(
    fname_pattern,
    engine='netcdf4',
    concat_dim="step",
    combine='nested',
    decode_timedelta=True,
    parallel=True
)

# Make sure forecast steps are sorted
forecast = forecast.sortby("step")


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
}

for var, attrs in var_attrs.items():
    if var in forecast:
        forecast[var].attrs.update(attrs)

# Add some global attributes (optional)
forecast.attrs.update({
    "description": "GEFSv12 reforecast IVT fields merged into a single file",
    "init_date": date,
})


# -----------------------------
# Rename dimension (if present)
# -----------------------------
if "time" in forecast.dims:
    forecast = forecast.rename({"time": "init_time"})


# -----------------------------
# Drop unneeded variables
# -----------------------------
forecast = forecast.drop_vars("surface", errors="ignore")


# -----------------------------
# Save to NetCDF
# -----------------------------
out_name = os.path.join(
    path_to_data,
    f"preprocessed/GEFSv12_reforecast/{varname}_final/GEFSv12_reforecast_IVT_{date}.nc"
)

forecast.load().to_netcdf(out_name, mode='w', format='NETCDF4')
print(f"Saved: {out_name}")