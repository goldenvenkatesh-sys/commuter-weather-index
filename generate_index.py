import requests
import json
from datetime import datetime

def calculate_two_wheeler_index():
    # Target cities for the dashboard
    cities = {
        "Chennai": {"lat": 13.0827, "lon": 80.2707},
        "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
        "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
        "Kochi": {"lat": 9.9312, "lon": 76.2673}
    }
    
    dashboard_data = {
        "update_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "locations": []
    }

    for city, coords in cities.items():
        # Pinging Open-Meteo's free, keyless API for ECMWF IFS model data
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current=precipitation,wind_gusts_10m&models=ecmwf_ifs04"
        
        try:
            response = requests.get(url)
            response.raise_for_status() # Check for HTTP errors
            data = response.json()
            
            # Extract live values
            precip_1hr = data['current']['precipitation']
            wind_gust = data['current']['wind_gusts_10m']
            
        except Exception as e:
            print(f"Failed to fetch data for {city}: {e}")
            precip_1hr = 0.0
            wind_gust = 0.0

        # Apply discrete logic thresholds for color boundaries
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

    # Export to JSON
    with open('commuter_index.json', 'w') as f:
        json.dump(dashboard_data, f, indent=4)
        
    print("Live ECMWF data fetched and dashboard updated successfully.")

if __name__ == "__main__":
    calculate_two_wheeler_index()
