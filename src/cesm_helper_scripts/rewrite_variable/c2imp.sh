#!/bin/sh

FILE="${1%.*}"

# From: https://code.mpimet.mpg.de/boards/1/topics/5213

cdo -selyear,1850 "$1" 1850.nc

cdo setyear,1 1850.nc 1_DataFile.nc
cdo setyear,9999 1850.nc 9999_DataFile.nc

cdo cat "*_DataFile.nc" "$FILE"_1_9999.nc

echo "$FILE"_1_9999.nc | python set_date_var_nc.py

mv "$FILE"_1_9999.nc interp_missing_months/
mv "$1" done/

# Then manually run ncks -A -v var1,var2,var3,... orig.nc new.nc
# where var1,... are variable without time dimension that was not included.
# Problably
# ncks -A -v P0,hyai,hyam,hybi,hybm in.nc out.nc
