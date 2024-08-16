from itertools import product
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
from zoneinfo import ZoneInfo
from tabulate import tabulate

# Replace with your actual Electricity Maps API token
API_KEY = 'YOUR_API_KEY'

def get_coordinates(city):
    """Fetch latitude and longitude of the city using geopy."""
    geolocator = Nominatim(user_agent="electricity_maps_app")
    try:
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"City '{city}' not found.")
            return None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None

def get_CO2_intensity_data(lat, lon):
    """Fetch electricity map CO2 intensity details for given latitude and longitude."""
    CO2_INTENSITY_URL = f"https://api.electricitymap.org/v3/carbon-intensity/latest?lat={lat}&lon={lon}"
    headers = {
        'auth-token': API_KEY
    }
    try:
        response = requests.get(CO2_INTENSITY_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching CO2 intensity data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error in accessing CO2 intensity data: {e}")
        return None

def get_power_breakdown(lat, lon):
    """Fetch power breakdown details for given latitude and longitude."""
    POWER_BREAKDOWN_URL = f"https://api.electricitymap.org/v3/power-breakdown/latest?lat={lat}&lon={lon}"
    headers = {
        'auth-token': API_KEY
    }
    try:
        response = requests.get(POWER_BREAKDOWN_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching power breakdown data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error in accessing power breakdown data: {e}")
        return None


def display_time(original_timestamp):
   # Convert the string to a datetime object
   parsed_datetime = datetime.strptime(original_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

   # Specify the desired time zone (e.g., UTC)
   tz = ZoneInfo("UTC")

   # Convert to UTC time (if it's not already in UTC)
   utc_datetime = parsed_datetime.astimezone(tz)

   # Format the datetime as desired
   formatted_utc_time = utc_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
   return formatted_utc_time


def main():
    city = input("Enter the name of a city: ").strip()
    if not city:
        print("City input cannot be empty.")
        return
    
   #Looking up coordinates for {city}
    coordinates = get_coordinates(city)
    
    if coordinates:
        lat, lon = coordinates
        print(f"\n{city} coordinates : Latitude {lat}, Longitude {lon}")
        
        #Displays the amount of CO2 emitted per kilowatt hour of electricity generated
        co2_data = get_CO2_intensity_data(lat, lon)
        
        if co2_data:
            print(f"\nElectricity Data for {city}:")
            print(f"\nAmount of CO2 emitted per kilowatt hour of electricity generated(CO2 Intensity) in {city}: {co2_data['carbonIntensity']} gCO2eq/kWh")
            print(f"Generated at: {display_time(co2_data['datetime'])}")

        else:
            print(f"Failed to fetch electricity data for {city}.")
        
        print(f"\nPower breakdown data for {city}:")
        power_data = get_power_breakdown(lat, lon)
        
        if power_data:
         power_breakdown = power_data['powerProductionBreakdown']
            
         # Display fossilFreePercentage
         print(f"\nPercentage of energy generated from fossil free sources: {power_data['fossilFreePercentage']}%")

         # Calculate power production breakdown in watts and percentage
         total_production = power_data['powerProductionTotal']
         production_breakdown = [
             [source, production if production is not None else 0, f"{((production if production is not None else 0) / total_production) * 100:.2f}%"]
         for source, production in power_data['powerProductionBreakdown'].items()
         ]
         production_breakdown.sort(key=lambda x: x[1], reverse=True)
            
         print("\nPower Production Breakdown:")
         print(tabulate(production_breakdown, headers=["Power Source", "Watts", "Percentage"], tablefmt="pretty"))
        else:
            print(f"Failed to fetch power breakdown data for {city}.")
    
    else:
        print(f"Could not find coordinates for {city}.")
        main()

if __name__ == "__main__":
    main()