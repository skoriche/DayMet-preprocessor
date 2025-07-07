#!/bin/bash
# This is an example script to subset and download Daymet gridded daily data utilizing the netCDF Subset Service RESTful API 
# available through the ORNL DAAC THREDDS Data Server
#
# Daymet data and an interactive netCDF Subset Service GUI are available from the THREDDS web interface:
# https://thredds.daac.ornl.gov/thredds/catalogs/ornldaac/Regional_and_Global_Data/DAYMET_COLLECTIONS/DAYMET_COLLECTIONS.html
#
# Usage:  This is a sample script and not intended to run without user updates.
# Update the inputs under each section of "VARIABLES" for temporal, spatial, and Daymet weather variables.
# More information on Daymet NCSS gridded subset web service is found at:  https://daymet.ornl.gov/web_services
#
# The current Daymet NCSS has a size limit of 6GB for each single subset request. 
#
# Daymet dataset information including citation is available at:
# https://daymet.ornl.gov/
#
# modefied by Sifan A. Koriche from Michele Thornton (ORNL DAAC) June 30, 2025(https://github.com/ornldaac/gridded_subset_example_script)
#
#################################################################################
# VARIABLES - Temporal subset - This example is set to full Daymet calendar years
# Note:  The Daymet calendar is based on a standard calendar year. All Daymet years have 1 - 365 days, including leap years. For leap years, 
# the Daymet database includes leap day. Values for December 31 are discarded from leap years to maintain a 365-day year.
#################################################################################
# --- CONFIGURATION ---

# Set the target directory for downloaded files.
# This path is relative to the location of the script itself.
# It assumes the script is in '1_data_download/'.
OUTPUT_DIR="$(dirname "$0")/../data/raw/daymet"

# VARIABLES - Temporal subset
startyr=2023
endyr=2023

# VARIABLES - Region
region="na"

# VARIABLES - Daymet variables
var="tmin tmax prcp srad vp swe"

# VARIABLES - Spatial subset - bounding box for GSL
north=42.85
west=-113.50
east=-110.40
south=39.60
################################################################################

# --- EXECUTION ---

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"
echo "Files will be downloaded to: $OUTPUT_DIR"

for ((i=startyr;i<=endyr;i++)); do
    echo "--- Processing Year: $i ---"
    for par in $var; do
        echo "  Downloading: $par"
        
        # Define the full path for the output file
        output_file="${OUTPUT_DIR}/${par}_${i}subset.nc"
        
        # Daymet calendar has 365 days. For leap years, Dec 31 is omitted.
        if [ $(( $i % 4 )) -eq 0 ]; then
            # Leap year: end date is 12-30
            wget -q --show-progress -O "$output_file" "https://thredds.daac.ornl.gov/thredds/ncss/grid/ornldaac/2129/daymet_v4_daily_${region}_${par}_${i}.nc?var=lat&var=lon&var=${par}&north=${north}&west=${west}&east=${east}&south=${south}&horizStride=1&time_start=${i}-01-01T12:00:00Z&time_end=${i}-12-30T12:00:00Z&timeStride=1&accept=netcdf"
        else
            # Common year: end date is 12-31
            wget -q --show-progress -O "$output_file" "https://thredds.daac.ornl.gov/thredds/ncss/grid/ornldaac/2129/daymet_v4_daily_${region}_${par}_${i}.nc?var=lat&var=lon&var=${par}&north=${north}&west=${west}&east=${east}&south=${south}&horizStride=1&time_start=${i}-01-01T12:00:00Z&time_end=${i}-12-31T12:00:00Z&timeStride=1&accept=netcdf"
        fi
    done;
done

echo "--- Download complete. ---"
