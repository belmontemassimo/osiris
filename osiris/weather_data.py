import requests
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime, timezone
import time


def get_coords():
    for i in range (5):
        try:
            url = 'http://ipinfo.io/json?token=0b62e80768fe36'
            response = urlopen(url)
            data = json.load(response)
            coords = data['loc'].split(',')
            return coords[0],coords[1]
        
        except HTTPError as e:
            wait_time = 2 ** i  # Exponential backoff
            print(f"Rate limited. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        except Exception:
            print('coords not reachable')
            return None
        

def get_today_weather():

    forecast_data = get_weather_data()
    forecast_data = forecast_data['daily'][0]
    avg_temp = forecast_data['temp']['day']
    weather = forecast_data['weather'][0]['main']    
    
    return avg_temp, weather




def get_weather_data(key = 'e4c65e61c4cb0bd79ccacb75d34e5efa'):
    try:
        lat, lon = get_coords()
        key = 'e4c65e61c4cb0bd79ccacb75d34e5efa'
        url =  f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&appid={key}'

        r = requests.get(url)
        temp = r.json()
        return temp
    
    except Exception:
        return None


def get_current_temp(key = 'e4c65e61c4cb0bd79ccacb75d34e5efa'):
    coords = get_coords()
    if coords:

        lat, lon = get_coords()
        key = 'e4c65e61c4cb0bd79ccacb75d34e5efa'
        url =  f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&appid={key}'

        r = requests.get(url)
        temp = r.json()['current']['temp']
        return temp

    else:
        return None

# Forecast of 7 coming days
def incoming_7_forecast():

    forecast_data = get_weather_data()

    forecast = {}

    if forecast_data:
        for day in forecast_data['daily']:
            today_unix = int(datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0).timestamp())
            if day['dt'] == today_unix:
                continue
            date = datetime.utcfromtimestamp(day['dt']).strftime('%Y-%m-%d')  # Unix timestamp
            temp_day = day['temp']['day']  # Daytime temperature
            weather = day['weather'][0]['description']  # Weather description
            forecast[date] = {"temp": temp_day, "weather": weather}

    else:
        return None
    
    return forecast

if __name__ == '__main__':
    print()
    temp, weather = get_today_weather()
    print(temp, weather)

    
    forecast = incoming_7_forecast()
    for day in forecast:
        print('\n',day,":")
        print(f"    Temperature: {forecast[day]['temp']}")
        print(f"    Weather: {forecast[day]['weather']}")

