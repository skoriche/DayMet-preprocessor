# Daymet Climate Data Preprocessor
This repository contains a complete workflow to download, subset, and process raw Daymet NetCDF climate data. It is designed to take raw climate data and transform it into clean, aggregated time-series CSV files suitable for analysis and as input for machine learning models. The primary output is a set of CSV files, one for each geographic sub-basin, where each column represents a climate variable and each row represents the daily spatial average for that variable.

## Directory Structure
The repository is organized into a sequential workflow:

```text
DayMet-preprocessor/
│
├── .gitignore
├── README.md
├── requirements.txt
│
├── 1_data_download/
│   └── download_daymet.sh
│
├── 2_data_preprocessing/
│   └── process_daymet_data.py
│
└── data/
    ├── raw/
    │   ├── daymet/
    │   │   ├── *_1980subset.nc  (Sample raw data)
    │   │   └── ...
    │   ├── shapefiles/
    │   │   └── ... (Your shapefile data goes here)
    │   └── DayMet-raw-ReadMe.md
    │
    └── processed/
        ├── timeseries_csv/
        │   ├── Bear_timeseries.csv
        │   └── ...
        └── DayMet-Processed-ReadMe.md
```


For detailed information on the data formats, variables, and units, please see the `README` files located in the `data/raw/DayMet-raw-ReadMe.md` and `data/processed/DayMet-Processed-ReadMe.md` directories.

## Setup and Installation

**1. Clone the Repository**
```bash

git clone https://github.com/skoriche/DayMet-preprocessor.git
cd DayMet-preprocessor

```

**2. Setup Python Environment**

# Create the virtual environment 
```bash
# Create the virtual environment
python -m venv .daymet_gsl_env

# Activate the environment [On many HPC systems, you must load the base Python module before activating your local environment.]
source .daymet_gsl_env/bin/activate

```

**3. Install Dependencies**

Install all required Python packages from the requirements.txt file.
```bash

pip install -r requirements.txt

```

## Workflow Execution

Follow these steps in order to generate the final time-series data.

**Step 1: Download Raw Data (Optional)**

The repository already includes sample data for 1980. To download additional years of data, run the download_daymet.sh script.

First, make the script executable:
```bash
chmod +x 1_data_download/download_daymet.sh
```

Then, run the script. It is pre-configured to download data for 1980-1982 but can be easily modified. Files will be saved into the data/raw/daymet/ directory.

```bash
# First, make the script executable
chmod +x 1_data_download/download_daymet.sh

# Then, run the script. It will automatically save files into the data/raw/daymet/ directory.
./1_data_download/download_daymet.sh
```

**Step 2: Preprocess Data**

Once the raw data is in place, run the `process_daymet_data.py` script to generate the final CSV files.
- Prerequisite: Ensure your sub-basin shapefile is located in the `data/raw/shapefiles/` directory.
- Input: Reads raw NetCDF files from `data/raw/daymet/`.
- Output: Saves processed CSV files to `data/processed/timeseries_csv/`.

```bash
python 2_data_preprocessing/process_daymet_data.py \
    --shapefile_path "./data/raw/shapefiles/GSLSubbasins_proj.shp" \
    --netcdf_directory "./data/raw/daymet/" \
    --output_directory "./data/processed/timeseries_csv/" \
    --shapefile_id_column "Name"
```

After running this command, the `data/processed/timeseries_csv/` directory will be populated with the final data.
