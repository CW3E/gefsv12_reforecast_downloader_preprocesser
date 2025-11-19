"""
Filename:    getGEFSv12_batch.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Download GEFSv12 Reforecast data based on input configuration dictionary.

"""
import sys
import yaml
import subprocess

sys.path.append('../modules')
import globalvars

### Imports config name from argument when submit
yaml_doc = sys.argv[1]
config_name = sys.argv[2]

# import configuration file for season dictionary choice
config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
ddict = config[config_name]

year = ddict['year']
date = ddict['date']
varname = ddict['varname']
path_to_data = globalvars.path_to_data + f"downloads/GEFSv12_reforecast/{date}/" # this is where the downloaded data will be saved
path_to_aws = globalvars.path_to_aws # this is that path of the awscli executable

## run download_GEFSv12_reforecast.sh to download data 
path_to_repo = globalvars.path_to_repo
bash_script = path_to_repo+"download_gefsv12/download_GEFSv12_reforecast.sh"
print(subprocess.run([bash_script, year, date, varname, path_to_data, path_to_aws]))