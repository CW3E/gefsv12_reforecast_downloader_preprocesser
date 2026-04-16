#!/bin/bash
#SBATCH --account=cwp140
#SBATCH --partition=shared-128
#SBATCH -N 1
#SBATCH --nodes=1
#SBATCH --mem=32GB
#SBATCH --job-name=concat_gefs_reforecast
#SBATCH --array=0-730%100 # each call runs 10 days - 7305 days / 10 ≈ 731 jobs
#SBATCH -o slurm_out/concat_%A_%a.out
#SBATCH -e slurm_out/concat_%A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=dnash@ucsd.edu

PYTHON="/home/dnash/miniconda3/envs/SEAK-impacts/bin/python"

$PYTHON concat_gefsv12_batch.py