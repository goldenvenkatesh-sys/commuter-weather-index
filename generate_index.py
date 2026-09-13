import xarray as xr
import numpy as np
import pandas as pd
import json
from datetime import datetime

def calculate_two_wheeler_index():
    # 1. Load your forecast data (replace with your actual file path or API pull)
    # ds = xr.open_dataset('latest_model_run.nc')
    
    # For demonstration, creating a dummy dataset mimicking ECMWF 1-hour data
    lats = np.arange(8.0, 20.5, 0.5)
    lons = np.arange(74.0, 85.5, 0.5)
    
    # 2. GEOGRAPHIC CONSTRAINT: Ensure we only process South India to keep file sizes tiny
    # If loading national data, use: ds = ds.sel(latitude=slice(20, 8), longitude=slice(74, 85))
    
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
        # 3. Extract nearest grid point data (mocked values here)
        # precip_1hr = ds.tp.sel(latitude=coords['lat'], longitude=coords['lon'], method='nearest').values
        # wind_gust = ds.fg10.sel(latitude=coords['lat'], longitude=coords['lon'], method='nearest').values
        
        # Simulating extracted data
        precip_1hr = np.random.uniform(0, 25) # mm/hr
        wind_gust = np.random.uniform(10, 55) # km/h
        visibility = np.random.uniform(2, 10) # km
        
        # 4. DISCRETE LOGIC: Map variables strictly to discrete color blocks (Green, Yellow, Red)
        if precip_1hr > 15 or wind_gust > 45 or visibility < 3:
            status = "Red"
            message = "Dangerous riding conditions. Heavy rain or severe gusts."
            hex_color = "#FF3B30"
        elif precip_1hr > 3 or wind_gust > 25 or visibility < 5:
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

    # 5. Export to a static JSON file for GitHub Pages to read
    with open('commuter_index.json', 'w') as f:
        json.dump(dashboard_data, f, indent=4)
        
    print("Dashboard data generated successfully.")

if __name__ == "__main__":
    calculate_two_wheeler_index()
