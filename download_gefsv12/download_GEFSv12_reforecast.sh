#!/bin/bash
######################################################################
# Filename:    download_GEFSv12_reforecast.sh
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to download GEFSv12 reforecast data
# https://registry.opendata.aws/noaa-gefs-reforecast/ (data link)
#
######################################################################

### Inputs
IN_YR=$1
IN_DATE=$2
VARNAME=$3
PATH_TO_OUT=$4
PATH_TO_AWS=$5

### Variables to download: 
if [ $VARNAME == 'ivt' ]; then
    var_array=(
    ugrd_pres ## U below 700 mb
    ugrd_pres_abv700mb ## U above 700 mb
    vgrd_pres ## V below 700 mb
    vgrd_pres_abv700mb ## V above 700 mb
    spfh_pres ## Q below 700 mb
    spfh_pres_abv700mb ## Q above 700 mb
    pres_sfc ## surface pressure - need this because GEFS puts values below the surface
    )
elif [ $VARNAME == 'qpf' ]; then
    var_array=(
    apcp_sfc ## Total Precipitation
    )
    
elif [ $VARNAME == 'freezing_level' ]; then
    var_array=(
    tmp_pres ## T below 700 mb
    tmp_pres_abv700mb ## T above 700 mb
    hgt_pres ## Z below 700 mb
    hgt_pres_abv700mb ## Z above 700 mb
    )
elif [ $VARNAME == 'uv' ]; then
    var_array=(
    # hgt_sfc ## surface height
    vgrd_pres ## V below 700 mb
    ugrd_pres ## U below 700 mb
    )
else
  echo "Variable not configured"
fi

ens_array=(
c00
p01
p02
p03
p04
)
# set up out path
mkdir -p ${PATH_TO_OUT}
echo ${PATH_TO_OUT}

## outer loop - loop through ensemble members
for i in ${!ens_array[*]}
do
    ENS="${ens_array[$i]}"
    ### Set up paths
    PATH_TO_DATA="s3://noaa-gefs-retrospective/GEFSv12/reforecast/${IN_YR}/${IN_DATE}00/${ENS}/Days:1-10/"

    ## inner loop - loop through variables

    for j in ${!var_array[*]}
    do
        VAR_NAME="${var_array[$j]}"

        ### Copy a single file from S3 to local

        INPUT_FNAME="${PATH_TO_DATA}${VAR_NAME}_${IN_DATE}00_${ENS}.grib2"
        OUTPUT_FNAME="${PATH_TO_OUT}${VAR_NAME}_${IN_DATE}00_${ENS}.grib2"
        # echo ${OUTPUT_FNAME}
        ${PATH_TO_AWS} s3 cp --region us-east-1 ${INPUT_FNAME} ${OUTPUT_FNAME} --no-sign-request

    done

done


