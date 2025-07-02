## Data Directory
This directory contains the raw and processed data for the project.

### Input Data - `raw/`
This subdirectory holds the original, unmodified input data.

### AOI (Boundary) Data - `raw/shapefiles/`
Contains the vector data (ESRI Shapefiles) defining the geographic boundaries of the sub-basins of interest (e.g., Great Salt Lake sub-basins).

### DayMet Data - `raw/daymet/`
Contains the raw Daymet Version 4 daily surface weather data, downloaded as NetCDF (.nc) files. This repository includes a sample of the data for the year 1980 for reproducibility.

### Daymet V4 Dataset Details
- Source - [Daymet: Daily Surface Weather and Climatological Summaries](https://daymet.ornl.gov/)
- Spatial Resolution: 1-km x 1-km grid
- Temporal Resolution: Daily
- Temporal Coverage: 1980 - present
- Spatial Coverage: North America, Hawaii, and Puerto Rico
- Projection: Lambert Conformal Conic

### Climate Variables
| Variable | Description | Units |
|----------|-------------|-------|
| tmin | Daily minimum air temperature | °C |
| tmax | Daily maximum air temperature | °C |
| prcp | Daily total precipitation | mm/day |
| srad | Shortwave radiation | W/m² |
| vp | Water vapor pressure | Pa |
| swe | Snow-water equivalent | kg/m² |
| dayl | Day length | seconds |
