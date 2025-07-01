# -*- coding: utf-8 -*-
"""
Processes a collection of Daymet NetCDF climate data files by extracting 
time-series data for geographic regions defined in a shapefile.

This script calculates the daily spatial average for each variable within each 
region and exports the results to separate CSV files.


Command to Run:
Execute the command from the root directory `DayMet-preprocessor`. The script will use 
relative paths to find the input data and save the output in the correct locations.

python 2_data_preprocessing/process_daymet_data.py \
    --shapefile_path "data/raw/shapefiles/GSLSubbasins_proj.shp" \
    --netcdf_directory "data/raw/daymet/" \
    --output_directory "dat/processed/timeseries_csv/" \
    --shapefile_id_column "Name"  #user defined
"""

import argparse
import pathlib
import sys
import geopandas
import pandas as pd
import xarray as xr
import rioxarray  # noqa: F401 - required for the .rio accessor

# Daymet data uses a Lambert Conformal Conic projection.
# We define its proj4 string here to ensure consistency. The units are meters.
DAYMET_CRS = "+proj=lcc +lat_1=25 +lat_2=60 +lat_0=42.5 +lon_0=-100 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs"

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process Daymet NetCDF data for sub-basins defined in a shapefile.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--shapefile_path",
        type=pathlib.Path,
        required=True,
        help="Full path to the input sub-basin shapefile."
    )
    parser.add_argument(
        "--netcdf_directory",
        type=pathlib.Path,
        required=True,
        help="Path to the directory containing all downloaded .nc files."
    )
    parser.add_argument(
        "--output_directory",
        type=pathlib.Path,
        required=True,
        help="Path to the directory where output CSV files will be saved."
    )
    parser.add_argument(
        "--shapefile_id_column",
        type=str,
        default='Subbasin',
        help="Attribute column in the shapefile with unique sub-basin names."
    )
    return parser.parse_args()

def process_subbasin(subbasin_name, subbasin_geometry, netcdf_dir):
    """
    Processes all NetCDF variables for a single sub-basin.

    For a given sub-basin geometry, this function finds all climate variables
    in the netcdf_dir, combines them by year, clips them to the geometry,
    calculates the daily spatial mean, and returns a single aggregated DataFrame.

    Args:
        subbasin_name (str): The name of the sub-basin being processed.
        subbasin_geometry (shapely.geometry): The geometry of the sub-basin.
        netcdf_dir (pathlib.Path): Path to the directory with NetCDF files.

    Returns:
        pandas.DataFrame: A DataFrame containing the daily time series for all
                          climate variables for the given sub-basin. Returns
                          None if no variables are found.
    """
    print(f"  Identifying climate variables for '{subbasin_name}'...")
    
    variable_stems = sorted(list(set(f.name.split('_')[0] for f in netcdf_dir.glob('*.nc'))))

    if not variable_stems:
        print(f"  Warning: No NetCDF files found in {netcdf_dir}. Skipping sub-basin.")
        return None

    print(f"  Found variables: {', '.join(variable_stems)}")
    
    basin_timeseries_list = []

    for stem in variable_stems:
        print(f"    Processing variable: {stem}...")
        
        netcdf_files = sorted(list(netcdf_dir.glob(f'{stem}_*.nc')))
        if not netcdf_files:
            continue

        # Using chunks={} disables Dask/parallel processing to prevent segfaults.
##        with xr.open_mfdataset(netcdf_files, combine='by_coords', chunks={}) as ds:
        with xr.open_mfdataset(netcdf_files, combine='by_coords', chunks={}, engine='netcdf4') as ds:
            
            # The NetCDF file's coordinates are in kilometers, but the CRS
            # definition expects meters. We must convert them to match.
            ds.coords['x'] = ds.coords['x'] * 1000
            ds.coords['y'] = ds.coords['y'] * 1000
            ds['x'].attrs['units'] = 'm'
            ds['y'].attrs['units'] = 'm'

            ds = ds.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=True)
            ds = ds.rio.write_crs(DAYMET_CRS, inplace=True)

            try:
                # The geometry is already in the correct CRS from the main function
                clipped_ds = ds.rio.clip([subbasin_geometry], all_touched=True, drop=True)
                
                # --- FINAL CLEANUP: Use .sizes to avoid FutureWarning ---
                if 'x' not in clipped_ds.sizes or 'y' not in clipped_ds.sizes or \
                   clipped_ds.sizes['x'] == 0 or clipped_ds.sizes['y'] == 0:
                    print(f"    Warning: Clipping for {stem} resulted in no data for {subbasin_name}. The sub-basin might be outside the data extent.")
                    continue

            except Exception as e:
                print(f"    Error clipping {stem} for {subbasin_name}: {e}")
                continue

            # Select the specific data variable and calculate the mean
            spatial_mean_da = clipped_ds[stem].mean(dim=['x', 'y'], keep_attrs=True)
            
            # Manually create the DataFrame to avoid extra metadata columns.
            ts_df = pd.DataFrame(
                spatial_mean_da.values,
                index=spatial_mean_da.coords['time'],
                columns=[stem]
            )

            basin_timeseries_list.append(ts_df)

    if not basin_timeseries_list:
        print(f"  Warning: No data could be processed for sub-basin '{subbasin_name}'.")
        return None

    print("    Aggregating all variables...")
    final_df = pd.concat(basin_timeseries_list, axis=1)
    return final_df


def main():
    """Main function to orchestrate the data processing workflow."""
    args = parse_arguments()

    if not args.shapefile_path.is_file():
        print(f"Error: Shapefile not found at '{args.shapefile_path}'")
        sys.exit(1)
    if not args.netcdf_directory.is_dir():
        print(f"Error: NetCDF directory not found at '{args.netcdf_directory}'")
        sys.exit(1)

    args.output_directory.mkdir(parents=True, exist_ok=True)
    print(f"Output will be saved to: {args.output_directory.resolve()}")

    print(f"\nLoading shapefile from: {args.shapefile_path.resolve()}")
    gdf = geopandas.read_file(args.shapefile_path)

    if args.shapefile_id_column not in gdf.columns:
        print(f"Error: ID column '{args.shapefile_id_column}' not found in shapefile.")
        print(f"Available columns are: {', '.join(gdf.columns)}")
        sys.exit(1)

    print(f"  Original shapefile CRS: {gdf.crs}")
    gdf = gdf.to_crs(DAYMET_CRS)
    print(f"  Reprojecting shapefile to Daymet CRS (e.g., WGS84 -> LCC)")
        
    print(f"\nFound {len(gdf)} sub-basins to process.")

    for row in gdf.itertuples():
        subbasin_name = getattr(row, args.shapefile_id_column)
        subbasin_geometry = row.geometry
        
        print(f"\nProcessing sub-basin: '{subbasin_name}'...")

        timeseries_df = process_subbasin(
            subbasin_name, subbasin_geometry, args.netcdf_directory
        )

        if timeseries_df is not None and not timeseries_df.empty:
            output_filename = f"{subbasin_name.replace(' ', '_').replace('/', '_')}_timeseries.csv"
            output_path = args.output_directory / output_filename
            
            print(f"  Writing file: {output_path}")
            timeseries_df.to_csv(output_path)
        else:
            print(f"  Skipping CSV export for '{subbasin_name}' due to processing issues.")

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()

