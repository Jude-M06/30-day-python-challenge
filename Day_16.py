#------------------
# use this command first:
# python -m pip install requests
#------------------
import argparse
import json
import time
import requests
from datetime import datetime
from pathlib import Path

CACHE_FILE     = Path("weather_cache.json")
CACHE_MINUTES  = 30
NOMINATIM_URL  = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
HEADERS        = {"User-Agent": "PythonWeatherCLI/1.0 (educational project)"}

WEATHER_CODES = {
    0:  ("Clear sky"       ),
    1:  ("Mainly clear"    ),
    2:  ("Partly cloudy"   ),
    3:  ("Overcast"        ),
    45: ("Foggy"           ),
    51: ("Light drizzle"   ),
    61: ("Slight rain"     ),
    63: ("Moderate rain"   ),
    65: ("Heavy rain"      ),
    71: ("Slight snow"     ),
    80: ("Rain showers"    ),
    95: ("Thunderstorm"    ),
}

def describe_weather(code):
    return WEATHER_CODES.get(code, ("Unknown"))

def geocode(city):
    resp = requests.get(NOMINATIM_URL, headers=HEADERS, timeout=10, params={
        "q": city, "format": "json", "limit": 1,
    })
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"City '{city}' not found.")
    return float(results[0]["lat"]), float(results[0]["lon"])

def fetch_weather(lat, lon):
    params = {
        "latitude":      lat,
        "longitude":     lon,
        "current":       "temperature_2m,apparent_temperature,"
                         "relative_humidity_2m,wind_speed_10m,weather_code",
        "daily":         "temperature_2m_max,temperature_2m_min,"
                         "precipitation_sum,weather_code",
        "forecast_days": 5,
        "timezone":      "auto",
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def get_weather_cached(city, lat, lon):
    cache = load_cache()
    key   = city.lower()
    now   = time.time()

    if key in cache:
        age_min = (now - cache[key]["fetched_at"]) / 60
        if age_min < CACHE_MINUTES:
            print(f"  (cached, {age_min:.0f} min old)")
            return cache[key]["data"]

    data = fetch_weather(lat, lon)
    cache[key] = {"fetched_at": now, "data": data}
    save_cache(cache)
    return data

def c_to_f(c):
    return c * 9/5 + 32

def print_current(city, data, units="metric"):
    curr        = data["current"]
    code        = curr["weather_code"]
    desc, emoji = describe_weather(code)
    temp        = curr["temperature_2m"]
    feels       = curr["apparent_temperature"]
    humid       = curr["relative_humidity_2m"]
    wind        = curr["wind_speed_10m"]

    temp_str  = f"{temp:.1f}°C"  if units == "metric" else f"{c_to_f(temp):.1f}°F"
    feels_str = f"{feels:.1f}°C" if units == "metric" else f"{c_to_f(feels):.1f}°F"
    wind_str  = f"{wind:.1f} km/h" if units == "metric" else f"{wind*0.621:.1f} mph"

    print("\n" + "-" * 42)
    print(f"  {emoji}  {city.title()} — {desc}")
    print("-" * 42)
    print(f"  Temperature  : {temp_str}")
    print(f"  Feels like   : {feels_str}")
    print(f"  Humidity     : {humid}%")
    print(f"  Wind speed   : {wind_str}")
    print("-" * 42)

def print_forecast(data, days=5, units="metric"):
    daily = data["daily"]
    print(f"\n  {'Date':<12} {'High':<10} {'Low':<10} {'Rain':<10} Sky")
    print("  " + "-" * 52)
    for i in range(min(days, len(daily["time"]))):
        date        = daily["time"][i]
        hi          = daily["temperature_2m_max"][i]
        lo          = daily["temperature_2m_min"][i]
        rain        = daily["precipitation_sum"][i]
        _, emoji    = describe_weather(daily["weather_code"][i])
        hi_s        = f"{hi:.0f}°C"    if units == "metric" else f"{c_to_f(hi):.0f}°F"
        lo_s        = f"{lo:.0f}°C"    if units == "metric" else f"{c_to_f(lo):.0f}°F"
        rain_s      = f"{rain:.1f}mm"  if units == "metric" else f"{rain*0.0394:.2f}in"
        label       = datetime.strptime(date, "%Y-%m-%d").strftime("%a %d %b")
        print(f"  {label:<12} {hi_s:<10} {lo_s:<10} {rain_s:<10} {emoji}")

def main():
    parser = argparse.ArgumentParser(description="Weather forecast CLI")
    parser.add_argument("city", nargs="?", help="City name")
    parser.add_argument("--days",    type=int, default=5)
    parser.add_argument("--units",   choices=["metric","imperial"], default="metric")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    city = args.city or input("Enter city: ").strip()
    if not city:
        print("No city provided.")
        return

    try:
        print(f"  Looking up '{city}'...")
        lat, lon = geocode(city)
        data = fetch_weather(lat, lon) if args.no_cache else get_weather_cached(city, lat, lon)
        print_current(city, data, args.units)
        print_forecast(data, args.days, args.units)
    except ValueError as e:
        print(f"  Error: {e}")
    except requests.RequestException as e:
        print(f"  Network error: {e}")

if __name__ == "__main__":
    main()
