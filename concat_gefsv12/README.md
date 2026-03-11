# Concatenate Preprocessed GEFSv12 Reforecast Data

This directory contains scripts to **concatenate preprocessed GEFSv12 Reforecast NetCDF files** across dates, ensemble members, and variables using **SLURM job arrays**. After preprocessing the raw data (see `../preprocess_gefsv12/`), these scripts combine the intermediate outputs into final analysis-ready datasets.

---

## Workflow Overview

1. **Edit concat_gefsv12_batch.py**

   * Edit `varname` to reflect the variable you are concatenating.
    
2. **Submit SLURM jobs**

   * Update `run_concat_GEFSv12_reforecast.slurm` to ensure #SBATCH --array=0-730%100
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
