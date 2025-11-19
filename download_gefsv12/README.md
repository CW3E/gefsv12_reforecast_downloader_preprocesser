# Download GEFSv12 Reforecast Data

This directory contains scripts to **download GEFSv12 Reforecast data** using Slurm job arrays. The data is accessed via `aws-cli` from the [NOAA GEFS Reforecast Open Data Registry](https://registry.opendata.aws/noaa-gefs-reforecast/).

---

## Downloadable Variable Sets

The scripts allow downloading the following variable sets for the **control** and **4 ensemble members** at all lead times:

1. **IVT**

   * Downloads u, v, q on all pressure levels and surface pressure.
   * Used to calculate Integrated Water Vapor Transport (IVT).

2. **Freezing Level**

   * Downloads geopotential height and temperature on all pressure levels.
   * Used to reverse interpolate the height of the 0°C isotherm.

3. **UV**

   * Downloads u and v wind components at pressure levels below 700 hPa.
   * Used to extrapolate u and v at specific pressure levels.

4. **QPF**

   * Downloads surface precipitation accumulation.

---

## Setup and Running Instructions

1. **Create job configuration files**

   * Edit `create_job_configs.py` to set `start_date` and `end_date` for your desired download range.
   * Run:

   ```bash
   conda activate gefs_reforecast_env
   python create_job_configs.py
   ```

   This generates `calls_varname_x.txt` and `config_varname_x.yaml` files for the Slurm job array.

2. **Make the download script executable**

   ```bash
   chmod +x download_GEFSv12_reforecast.sh
   ```

3. **Submit Slurm jobs**

   * Edit `run_download_GEFSv12_reforecast.slurm` to point to the correct `calls_varname_x.txt` file.
   * Submit the job array:

   ```bash
   sbatch run_download_GEFSv12_reforecast.slurm
   ```

---

## Notes

* Ensure your `aws-cli` is configured and has access to the GEFS Reforecast dataset.
* Each Slurm job will download files for a subset of dates and ensemble members as defined in the configuration files.
* Large downloads may require significant storage space; verify available disk capacity before starting.
* The downloaded files are GRIB2 format and will be processed in the `preprocess_gefsv12` workflow.
