*This README.md file was generated on 20251119 by Deanna Nash*

# General Information

---

### `GEFSv12_reforecast_{varname}_{date}.nc`

*Derived GEFSv12 Reforecast data.*

### Author Information

* Lead: Deanna Nash ([dnash@ucsd.edu](mailto:dnash@ucsd.edu))

### Date of data collection/creation

2023-10-01 to 2025-05-30

### Geographic location of data collection

North America and Pacific Ocean (10°N to 70°N, 60°W to 180°W)

### Funders and Sponsors of Data Collection

This research was supported by the National Science Foundation (NSF) Coastlines and People Program (award 2052972). Gunalchéesh to the Tlingit people for their stewardship of Lingít Aaní since time immemorial and today.

This work used the COMET, EXPANSE, and AWARE supercomputers, made available by the Atmospheric River Program supported by the California Department of Water Resources and the Forecast Informed Reservoir Operations Program supported by the U.S. Army Corps of Engineers Engineer Research and Development Center.

# Sharing/Access Information

---

### License & Restrictions on Data Reuse

Creative Commons Attribution 4.0 International (CC BY 4.0)

### Related Publications

> Nash, Deanna, Rutz, J.J., Jacobs, A., and Kawzenuk, B. (2025). “Using Model Climate to Improve Situational Awareness Ahead of Atmospheric River-Related Landslide Events in Southeast Alaska”. Submitted to: *Journal of Operational Meteorology*

### Links to Publicly Accessible Scripts to Download and Preprocess the Data

[https://github.com/CW3E/gefsv12_reforecast_downloader_preprocesser](https://github.com/CW3E/gefsv12_reforecast_downloader_preprocesser)

### Related Datasets

* NOAA Global Ensemble Forecast System, version 12 (GEFSv12) reforecast (retrospective forecasts) from 2000–2019 at 3-hour temporal resolution, downloaded via AWS: [NOAA GEFS Reforecast Open Data Registry](https://registry.opendata.aws/noaa-gefs-reforecast/).

# Data & File Overview

---

### File List

The files contain GEFSv12 Reforecast data for Integrated Water Vapor Transport (IVT) for each daily initialization date (YYYYMMDD) from 1 January 2000 to 31 December 2019:

```
.
├── GEFSv12_reforecast_IVT/
│   ├── GEFSv12_reforecast_IVT_20000101.nc
│   ├── GEFSv12_reforecast_IVT_YYYYMMDD.nc
└── └── GEFSv12_reforecast_IVT_20191231.nc
```

# File/Format-Specific Information

---

### `GEFSv12_reforecast_IVT/GEFSv12_reforecast_IVT_YYYYMMDD.nc`

* Number of variables: 3
* Number of lead times: 80

Variable details:

* **IVT** – Integrated Water Vapor Transport (kg m⁻¹ s⁻¹)
* **uIVT** – Zonal component of IVT (kg m⁻¹ s⁻¹)
* **vIVT** – Meridional component of IVT (kg m⁻¹ s⁻¹)
* **step** – Hours since initialization (every 3 hours out to 10 days)
* **init_time** – Initialization time (GEFSv12 Reforecast is initialized once per day)
* **valid_time** – Valid datetime for the forecast

# Methodological Information

---

GEFSv12 Reforecast data have 0.25°x0.25° horizontal resolution below 700 hPa and 0.5°x0.5° above 700 hPa. Pressure level data above 700 hPa were linearly interpolated to 0.25°x0.25° resolution to maintain consistent spatial resolution.

**IVT Calculation:**
Integrated Water Vapor Transport (IVT, kg m⁻¹ s⁻¹) was computed from interpolated u and v wind components (m s⁻¹) and specific humidity (kg kg⁻¹) at 12 pressure levels between 300 and 1000 hPa, masking out values below surface pressure.


<!-- **Freezing Level Calculation:**
The height of the freezing level was determined by reverse interpolating temperature (°C) to find the geopotential height (m) of the 0°C isotherm below 200 hPa. In cases of multiple 0°C layers (temperature inversions), the lowest geopotential height was used. Locations where the entire column remained below 0°C were flagged as missing.
 -->
