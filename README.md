# GEFSv12 Reforecast Download and Preprocessing Toolkit

This repository provides a set of scripts for **downloading**, **preprocessing**, and **concatenating** selected variables from the **GEFSv12 Reforecast** dataset. The processed outputs include:

* Integrated Water Vapor Transport (**IVT**)
* Freezing-level height
* U and V wind components at specified pressure levels
* Quantitative Precipitation Forecast (**QPF**)

The scripts are organized into sequential workflow stages, from data acquisition to post-processed analysis-ready files.

---

## Repository Structure

```
download_gefsv12/    # Scripts to pull GEFSv12 Reforecast GRIB2 files from AWS
preprocess_gefsv12/  # Scripts to regrid, subset, and compute derived variables
concat_gefsv12/      # Scripts to merge processed files across dates/ensembles
modules/             # Shared utilities, global variables, IO helpers
```

---

## Requirements

* Python environment with dependencies listed in your environment file (e.g., xarray, cfgrib, eccodes, boto3 if needed)
* AWS CLI installed and configured
* Sufficient storage (GEFSv12 can be large)

---

## Setup Instructions

1. **Install AWS CLI**
   Follow installation instructions at AWS documentation and verify credentials if required.

2. **Edit paths in `modules/globalvars.py`**
   Update download directories, output directories, and temporary paths to match your local or cluster environment.

3. **Download GEFSv12 Reforecast data**
   Run the scripts in the `download_gefsv12` directory to retrieve the raw GRIB2 files from AWS.

4. **Preprocess the downloaded data**
   Use the scripts in the `preprocess_gefsv12` directory to:

   * Regrid data
   * Subset to a region of interest
   * Compute derived variables (IVT, freezing level, etc.)
   * Convert precipitation accumulations to hourly values

5. **Concatenate outputs**
   Run the scripts in `concat_gefsv12` to merge processed files by date, ensemble member, or variable, depending on your workflow.

---

## Notes

* Some variables require combining pressure-level files at different native resolutions (e.g., 0.25° vs 0.5°). The preprocessing scripts include logic to regrid and stitch these layers.
* Ensure your environment includes `eccodes` with GRIB support (`cfgrib` engine).
* For cluster workflows, consider using job arrays to parallelize across dates or ensemble members.
