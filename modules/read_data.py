"""
Filename:    io.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for reading GEFSv12 cfgrib data 
"""

import os, sys
import numpy as np
import xarray as xr
import glob
from functools import partial
from pathlib import Path
import globalvars

path_to_data = globalvars.path_to_data

def get_download_path(date):
    return Path(path_to_data) / "downloads" / "GEFSv12_reforecast" / date
    
def fix_longitude(ds):
    """Convert longitude from 0..360 to -180..180.


    Returns a dataset with corrected longitude coordinates.
    """
    return ds.assign_coords(
        longitude=((ds.longitude + 180) % 360) - 180
    )

def subset_na(ds):
    return ds.sel(latitude=slice(70, 0), longitude=slice(-179.5, -60.))

def clean_coords(ds):
    return subset_na(fix_longitude(ds))

def align_timesteps(ds1, ds2):
    """Return ds1, ds2 with matching step dimension length."""
    n1, n2 = ds1.step.size, ds2.step.size
    if n1 > n2:
        ds2 = ds1.reindex_like(ds2, method="pad", fill_value=np.nan)
    elif n2 > n1:
        ds1 = ds2.reindex_like(ds1, method="pad", fill_value=np.nan)
    return ds1, ds2

def preprocess(ds, start, stop):
    '''keep only selected time step hours'''
    return ds.isel(step=slice(start, stop))

def _preprocess(x, start, stop):
    if x['time'].size > 1:
            x = x.isel(time=0)
    return x.isel(step=slice(start, stop))
    
def safe_open_mfdataset(pattern, engine, concat_dim, combine, preprocess):
    """Try to open multiple files with xarray, falling back to a custom fixer.
    
    
    This encapsulates the repeated try/except that arises from cfgrib/cfconventions
    quirks across GEFSv12 files.
    """
    
    pattern = str(pattern)
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matched pattern: {fname}")
    try:
        return xr.open_mfdataset(files, engine=engine, concat_dim=concat_dim, combine=combine,
        preprocess=preprocess, decode_timedelta=True,)
    except (ValueError, TypeError) as exc:
        logger.warning("open_mfdataset failed for %s (%s). Using fallback.", pattern, exc)
        return fix_GEFSv12_open_mfdataset(files, preprocess)


def fix_GEFSv12_open_mfdataset(pattern, preprocess):
    """Fallback routine to emulate open_mfdataset when files have different steps.
    
    
    The function finds all matching files, opens them individually, standardizes
    the `valid_time` coordinate to the longest-duration file, and concatenates
    along `number`.
    """
    pattern = str(pattern)
    files = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No files matched pattern: {pattern}")
    
    ds_list: list[xr.Dataset] = []
    for fn in files:
        ds = xr.open_dataset(fn, engine="cfgrib", decode_timedelta=True)
        if "time" in ds and ds["time"].size > 1:
            ds = ds.isel(time=0)
        ds_list.append(ds)
    
    
    # Find dataset with the largest step dimension and use its valid_time
    step_sizes = [ds.step.size for ds in ds_list]
    idx_max = int(np.argmax(step_sizes))
    max_ds = ds_list[idx_max]
    max_time = max_ds.valid_time.values
    
    
    new_list = []
    for ds in ds_list:
        if ds.step.size < max_ds.step.size:
            new_ds = ds.reindex_like(max_ds, method="nearest", fill_value=np.nan)
            new_ds = new_ds.assign_coords(valid_time=("step", max_time))
            new_ds = _preprocess(new_ds, 0, max_ds.step.size)
            new_list.append(new_ds)
        else:
            new_list.append(_preprocess(ds, 0, max_ds.step.size))
    
    
    out = xr.concat(new_list, dim="number")
    
    return out

def load_pressure_level_variable(varname, date, start, stop):
    """
    Read GEFSv12 pressure-level data above and below 700 hPa, regrid the upper levels,
    and return a single merged dataset on a uniform 0.25° grid.

    Parameters
    ----------
    varname : str
        Variable name prefix used in the GEFS file naming convention (e.g., 'ugrd', 'vgrd').
    date : str
        Forecast initialization date in YYYYMMDD format.
    start : int
        Starting index in the "step" dimension for slicing time.
    stop : int
        Ending index in the "step" dimension for slicing time.

    Returns
    -------
    xr.Dataset
        Dataset containing the combined above- and below-700-hPa fields on the
        unified 0.25° grid, subset to North America and with longitudes in [-180, 180].
    """
    path_to_downloads = get_download_path(date)
    # Below 700 hPa files are already on the 0.25° grid
    fname = path_to_downloads / f"{varname}_pres_{date}00*.grib2"
    partial_func = partial(_preprocess, start=start, stop=stop)
    ds_below = safe_open_mfdataset(fname, engine="cfgrib", concat_dim="number", combine="nested", preprocess=partial_func)
        
    # Above 700 hPa files are on a coarser 0.50° grid and require regridding
    fname = path_to_downloads / f"{varname}_pres_abv700mb_{date}00_*.grib2"
    ds_above = safe_open_mfdataset(fname, engine="cfgrib", concat_dim="number", combine="nested", preprocess=partial_func)
    
    ## regrid ds_above to same horizontal resolution as ds_below
    regrid_lats = ds_below.latitude.values
    regrid_lons = ds_below.longitude.values
    ds_above = ds_above.interp(longitude=regrid_lons, latitude=regrid_lats)

    ## check for matching sizes
    nsteps_above = ds_above.step.size
    nsteps_below = ds_below.step.size

    ds_below, ds_above = align_timesteps(ds_below, ds_above)
    
    ## concatenate into single ds
    ds = xr.concat([ds_below, ds_above], dim='isobaricInhPa')

    ## now we can delete ds_below and ds_above since we are done with them
    del ds_above, ds_below
    
    ds = clean_coords(ds)

    return ds

def load_surface_variable(varname, date, start, stop):
    '''
    Using xarray, reads grib data for given variable for surface level data
    Concatenated along ensemble axis
    
    returns: ds
        xarray dataset of variable at 0.25 degree horizonal resolution for all times
    '''
    
    # read surfaced data
    path_to_downloads = get_download_path(date)
    fname = path_to_downloads / f"{varname}_{date}00*.grib2" 
    partial_func = partial(_preprocess, start=start, stop=stop)

    ds = safe_open_mfdataset(fname, engine="cfgrib", concat_dim="number", combine="nested", preprocess=partial_func)

    ds = clean_coords(ds)
    
    return ds