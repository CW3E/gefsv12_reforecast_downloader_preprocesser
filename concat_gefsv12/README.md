# Concatenate Preprocessed GEFSv12 Reforecast Data

This directory contains scripts to **concatenate preprocessed GEFSv12 Reforecast NetCDF files** across dates, ensemble members, and variables using **SLURM job arrays**. After preprocessing the raw data (see `../preprocess_gefsv12/`), these scripts combine the intermediate outputs into final analysis-ready datasets.

---

## Workflow Overview

1. **Create job configuration files**

   * Use `create_job_configs.py` to generate `.txt` and `.yaml` files for batching concatenation jobs via SLURM.
   * Edit `start_date` and `end_date` to specify the range of dates to concatenate.
   * Run:

   ```bash
   conda activate gefs_reforecast_env
   python create_job_configs.py
   ```

   This generates `calls_varname_x.txt` and `config_varname_x.yaml` files for the SLURM job array.

2. **Submit SLURM jobs**

   * Update `run_concat_GEFSv12_reforecast.slurm` to point to the correct `calls_varname_x.txt` file.
   * Submit the job array:

   ```bash
   sbatch run_concat_GEFSv12_reforecast.slurm
   ```

   Each job concatenates files for a specific variable, date range, and ensemble subset.

---

## Notes

* Ensure all preprocessed files for the requested dates and ensemble members exist.
* Filenames and directory structure must match the conventions from `preprocess_gefsv12`.
* Large concatenations may require significant memory and disk space. Consider splitting jobs into smaller chunks if necessary.
* Final NetCDF files are saved in a structured output directory and are ready for analysis or downstream workflows.

---
