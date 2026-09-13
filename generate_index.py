import xarray as xr
import pandas as pd
import json
from datetime import datetime
import os

def calculate_two_wheeler_index():
    # 1. Define the input file
    # Ensure your GitHub Action downloads your .nc file to this directory first,
    # or point this to your actual WeatherNext/ECMWF data path.
    file_path = 'latest_model_run.nc'
    
    # Fallback to prevent GitHub Actions from failing if the file isn't uploaded yet
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Ensure the automated pipeline downloads the .nc file before running this script.")
        return

    # 2. Load the NetCDF dataset
    ds = xr.open_dataset(file_path)
    
    # 3. Constrain geographic extent to South India to reduce memory usage
    # Note: ECMWF latitudes are typically descending (90 to -90), so slice(20, 8) is used. 
    # If your specific model uses ascending latitudes, swap to slice(8, 20).
    try:
        ds_south_india = ds.sel(latitude=slice(20, 8), longitude=slice(74, 85))
    except Exception as e:
        print("Could not slice coordinates. Check if your dataset uses 'lat'/'lon' instead of 'latitude'/'longitude'.")
        ds_south_india = ds # Fallback to full grid if slicing fails

    # Target cities for the layman dashboard
    cities = {
        "Chennai": {"lat": 13.08, "lon": 80.27},
        "Bengaluru": {"lat": 12.97, "lon": 77.59},
        "Coimbatore": {"lat": 11.01, "lon": 76.95},
        "Kochi": {"lat": 9.93, "lon": 76.26}
    }
    
    dashboard_data = {
        "update_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "locations": []
    }

    for city, coords in cities.items():
        try:
            # 4. Extract nearest grid point data
            # Adjust 'tp' (Total Precipitation) and 'fg10' (10m Wind Gust) if your model uses different variable names (e.g., 'prcp', 'gust')
            precip_raw = ds_south_india['tp'].sel(latitude=coords['lat'], longitude=coords['lon'], method='nearest').values
            wind_raw = ds_south_india['fg10'].sel(latitude=coords['lat'], longitude=coords['lon'], method='nearest').values
            
            # ECMWF stores precipitation in meters; convert to mm
            precip_1hr = float(precip_raw) * 1000 
            
            # ECMWF stores wind gusts in m/s; convert to km/h
            wind_gust = float(wind_raw) * 3.6     
            
        except KeyError:
            # Fallback if variables aren't found in the dataset
            print(f"Variables 'tp' or 'fg10' not found for {city}.")
            precip_1hr = 0.0
            wind_gust = 0.0

        # 5. Apply discrete logic thresholds for color boundaries
        if precip_1hr > 15 or wind_gust > 45:
            status = "Red"
            message = "Dangerous riding conditions. Heavy rain or severe gusts."
            hex_color = "#FF3B30"
        elif precip_1hr > 3 or wind_gust > 25:
            status = "Yellow"
            message = "Caution advised. Take rain gear and expect slippery roads."
            hex_color = "#FFCC00"
        else:
            status = "Green"
            message = "Clear conditions for two-wheelers."
            hex_color = "#34C759"
            
        dashboard_data["locations"].append({
            "city": city,
            "precip_mm": round(precip_1hr, 1),
            "wind_kmh": round(wind_gust, 1),
            "status": status,
            "color_code": hex_color,
            "advice": message
        })

    # 6. Export to JSON
    with open('commuter_index.json', 'w') as f:
        json.dump(dashboard_data, f, indent=4)
        
    print("Dashboard data generated successfully from model data.")
    ds.close()

if __name__ == "__main__":
    calculate_two_wheeler_index()
