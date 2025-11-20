#!/bin/bash
#SBATCH --account=cwp140
#SBATCH --partition=shared-128
#SBATCH -N 1
#SBATCH --nodes=1
#SBATCH --mem=32GB
#SBATCH -o slurm_out/concat_out_%a
#SBATCH -e slurm_out/concat_err_%a
#SBATCH --job-name=concat_gefs_reforecast
#SBATCH --mail-type=ALL
#SBATCH --mail-user=dnash@ucsd.edu
#SBATCH --array=1-999%100 

# Activate conda environment
source /home/dnash/miniconda3/etc/profile.d/conda.sh
conda activate SEAK-impacts

linevar=`sed $SLURM_ARRAY_TASK_ID'q;d' calls_ivt_1.txt`
eval $linevar
