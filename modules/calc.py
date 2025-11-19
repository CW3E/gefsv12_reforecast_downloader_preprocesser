"""
Filename:    calc.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for preprocessing GEFSv12 reforecast data
"""

import os, sys
import numpy as np
import pandas as pd
import xarray as xr
from datetime import timedelta
from scipy.integrate import trapezoid
from wrf import interplevel
import glob
import re
from functools import partial
from pathlib import Path

import read_data as io


    
# ----------------------------- QPF processing -----------------------------
def convert_accum_precip_to_hourly(ds: xr.Dataset) -> xr.Dataset:
    """Convert accumulated precipitation (tp) into *incremental* precipitation.
    
    
    The GEFS reforecast files contain accumulated precipitation with a mixture
    of 3- and 6-hourly steps. This function extracts correct 3-hour values and
    computes 6-hour increments from differences, then merges them.
    """
    tp = ds["tp"] 
    
    # Timedelta-based step indices used in original script
    ts_3hr = pd.timedelta_range(start="0 day", periods=57, freq="3H")
    ts_6hr = pd.timedelta_range(start="0 day", periods=29, freq="6H")
    
    
    # The original code used slices like [1::2] and [1:] — preserve that logic
    prec_3hr = tp.sel(step=ts_3hr[1::2])
    tp_diff = tp.diff(dim="step")
    prec_6hr = tp_diff.sel(step=ts_6hr[1:])
    
    
    new_prec = prec_3hr.combine_first(prec_6hr)
    new_prec.name = "tp"
    
    
    ds = ds.drop_vars(["tp"])
    ds = xr.merge([ds, new_prec])
    return ds

def process_qpf(date):
    """Process accumulated precip into hourly series."""
    path_downloads = get_download_path(date)
    ctrl_file = path_downloads / f"apcp_sfc_{date}00_c00.grib2"
    ens_pattern = str(path_downloads / f"apcp_sfc_{date}00_p*.grib2")

    # Load control
    dsa = xr.open_dataset(ctrl_file, engine="cfgrib",
                          filter_by_keys={"dataType": "cf"}).expand_dims("number")

    # Load ensemble members
    dsb = xr.open_mfdataset(ens_pattern, engine="cfgrib",
                            concat_dim="number", combine="nested",
                            filter_by_keys={"dataType": "pf"})

    # Combine control + members
    ds = xr.concat([dsa, dsb], dim="number", coords="minimal", compat="override")

    # Fix longitude and subset domain
    ds = io.clean_coords(ds)

    # Convert accumulated precip → hourly
    ds = convert_accum_precip_to_hourly(ds)

    return ds
    
# --------------------- IVT preprocessing -------------------------
def calc_IVT_manual(ds):
    '''
    Calculate IVT manually (not using scipy.integrate)
    This is in case you need to remove values below the surface
     '''
    if ds.valid_time.size > 8:
        valid_times = ds.valid_time.isel(isobaricInhPa=0).values
    else:
        valid_times = ds.valid_time.values
    pressure = ds.isobaricInhPa.values*100 # convert from hPa to Pa
    dp = np.diff(pressure) # delta pressure
    g = 9.81 # gravity constant
    
    qu_lst = []
    qv_lst = []
    # enumerate through pressure levels so we select the layers
    for i, pres in enumerate(ds.isobaricInhPa.values[:-1]):
        pres2 = ds.isobaricInhPa.values[i+1]
        tmp = ds.sel(isobaricInhPa=[pres, pres2]) # select layer
        tmp = tmp.mean(dim='isobaricInhPa', skipna=True) # average q, u, v in layer
        # calculate ivtu in layer
        qu = ((tmp.q*tmp.u*dp[i])/g)*-1
        qu_lst.append(qu)
        # calculate ivtv in layer
        qv = ((tmp.q*tmp.v*dp[i])/g)*-1
        qv_lst.append(qv)
    
    ## add up u component of ivt from each layer
    qu = xr.concat(qu_lst, pd.Index(pressure[:-1], name="pres"))
    qu = qu.sum('pres')
    qu.name = 'ivtu'
    
    # ## add up v component of ivt from each layer
    qv = xr.concat(qv_lst, pd.Index(pressure[:-1], name="pres"))
    qv = qv.sum('pres')
    qv.name = 'ivtv'
    
    ## calculate IVT magnitude
    ivt = np.sqrt(qu**2 + qv**2)
    ivt.name = 'ivt'

    ds = xr.merge([qu, qv, ivt])
    ds = ds.assign_coords({'valid_time': (['step'], valid_times)})
    
    return ds
    
def load_ivt_inputs(date, year, start, stop):
    
    print('Loading u, v, and q pressure level data ....')
    varname_lst = ['ugrd', 'vgrd', 'spfh']
    ds_lst = []
    for i, varname in enumerate(varname_lst):
        ds = io.load_pressure_level_variable(varname, date, start, stop)
        ds_lst.append(ds)
    
    ## load in surface pressure
    print('Loading surface pressure data ....')
    ds_pres = io.load_surface_variable('pres_sfc', date, start, stop)
    ds_lst.append(ds_pres)
    
    ds = xr.merge(ds_lst) # merge u, v, and q into single ds
    ds = ds.sel(isobaricInhPa=slice(300, 1000))
    ds = ds.reindex(isobaricInhPa=ds.isobaricInhPa[::-1])
    
    ## mask values below surface pressure
    print('Masking values below surface ....')
    varlst = ['q', 'u', 'v']
    for i, varname in enumerate(varlst):
        ds[varname] = ds[varname].where(ds[varname].isobaricInhPa < ds.sp/100., drop=False)
    
    ## integrate to calculate IVT
    print('Calculating IVT ....')
    ds_IVT = calc_IVT_manual(ds) # calculate IVT
    
    return ds_IVT

# --------------------- Freezing Level preprocessing -------------------------
def calc_freezing_level(ds):
    ''' 
    This takes an xarray dataset with geopotential height and temperature at pressure levels
    and reverse interpolates temperature to find the geopotential height of the 0*C isotherm
    
    Returns: ds
        xarray dataset of freezing level (m) at 0.25 degree horizonal resolution
    '''
    
    ## need 2 3D arrays for input
    ## reshape output arrays
    ninit, ntime, nlev, nlat, nlon = ds.gh.shape
    gh = ds.gh.values
    t = ds.t.values-273.15 # convert to *C

    # interpolate gh to temperature = 0
    interp_var = interplevel(gh, t, [0])

    # put into a dataset
    lat = ds.latitude.values
    lon = ds.longitude.values
    print(interp_var.values.shape)

    var_dict = {'freezing_level': (['number', 'step', 'lat', 'lon'], interp_var.values)}
    ds = xr.Dataset(var_dict,
                    coords={'number': (['number'], ds.number.values),
                            'step': (['step'], ds.step.values),
                            'lat': (['lat'], lat),
                            'lon': (['lon'], lon),
                            'valid_time': (['step'], ds.valid_time.values)})

    return ds

def load_freezing_inputs(date, year, start, stop):
    print('Loading tmp and hgt data ....')
    varname_lst = ['tmp', 'hgt']
    ds_lst = []
    for varname in varname_lst:
        ds = io.load_pressure_level_variable(varname, date, start, stop)
        ds_lst.append(ds)

    ds = xr.merge(ds_lst) # merge tmp and hgt data
    ds = ds.sel(isobaricInhPa=slice(1000, 200)) ## only interested in freezing level below 200 hPa
    ds = calc_freezing_level(ds) # calculate freezing level (m)

    return ds

# --------------------- UV single level preprocessing -------------------------
def load_uv_inputs(date, year, start, stop, pres_level):
    print('Loading u and v data ....')
    if pres_level > 700.:   
        varname_lst = ['ugrd_pres', 'vgrd_pres']
    elif pres_level < 700.:
        varname_lst = ['ugrd_pres_abv', 'vgrd_pres_abv']
    ds_lst = []
    
    for varname in varname_lst:
        ds = io.load_surface_variable(varname, date, start, stop)
        ds = ds.sel(isobaricInhPa=pres_level)
        ds_lst.append(ds)
        
    ds = xr.merge(ds_lst) # merge u and v into single ds

    return ds
