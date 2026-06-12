"""
modules/weather.py

Module to fetch weather forecast data from OpenWeatherMap API and generate weather-related
farming recommendations using an LLM.
"""

import requests
import datetime
from config import WEATHER_API_BASE
from utils.llm_client import get_response, get_language_instruction

def get_weather(district: str, weather_api_key: str) -> dict:
    """
    Fetches the 7-day weather forecast for the specified district.
    If the API key is missing or the request fails, returns realistic mock weather data.

    Parameters:
        district (str): The district name.
        weather_api_key (str): OpenWeatherMap API key.

    Returns:
        dict: A dictionary containing:
            - "location": Location name (district).
            - "forecast": A list of 7 dictionaries containing day forecast info.
            Or {"error": "..."} in case of system failure.
    """
    try:
        # Check if API key is missing or empty
        if not weather_api_key or weather_api_key.strip() == "":
            return _generate_mock_weather(district)

        # Call OpenWeatherMap Forecast API
        url = f"{WEATHER_API_BASE}/forecast"
        params = {
            "q": f"{district},IN",
            "appid": weather_api_key,
            "units": "metric",
            "cnt": 7
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            # If the API call fails, fallback to mock data
            return _generate_mock_weather(district)

        data = response.json()
        location = data.get("city", {}).get("name", district)
        forecast_list = data.get("list", [])
        
        forecast = []
        for item in forecast_list:
            dt = item.get("dt")
            date_str = datetime.datetime.fromtimestamp(dt).strftime("%d %b") if dt else "N/A"
            
            temp_max = float(item.get("main", {}).get("temp_max", 0))
            temp_min = float(item.get("main", {}).get("temp_min", 0))
            humidity = int(item.get("main", {}).get("humidity", 0))
            wind_speed = float(item.get("wind", {}).get("speed", 0))
            
            # Weather description
            weather_desc = ""
            if item.get("weather") and len(item.get("weather")) > 0:
                weather_desc = item.get("weather")[0].get("description", "")
                
            # Rain volume (might be empty or missing)
            rain_mm = float(item.get("rain", {}).get("3h", 0.0))
            
            forecast.append({
                "date": date_str,
                "temp_max": temp_max,
                "temp_min": temp_min,
                "description": weather_desc,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "rain_mm": rain_mm
            })
            
        return {
            "location": location,
            "forecast": forecast
        }

    except Exception as e:
        # If any unexpected exception occurs during request, fallback to mock instead of crash
        try:
            return _generate_mock_weather(district)
        except Exception as fallback_err:
            return {"error": f"Failed to get weather: {str(e)}. Fallback failed: {str(fallback_err)}"}

def _generate_mock_weather(district: str) -> dict:
    """
    Generates realistic 7-day weather forecast mock data for Indian regions.
    """
    now = datetime.datetime.now()
    forecast = []
    
    # Selection of realistic descriptions, temps, and rain
    weather_patterns = [
        {"desc": "light rain", "tmax": 32, "tmin": 24, "humidity": 78, "wind": 12, "rain": 4.5},
        {"desc": "moderate rain", "tmax": 31, "tmin": 23, "humidity": 82, "wind": 14, "rain": 12.0},
        {"desc": "thunderstorm", "tmax": 29, "tmin": 22, "humidity": 88, "wind": 18, "rain": 25.4},
        {"desc": "partly cloudy", "tmax": 34, "tmin": 25, "humidity": 65, "wind": 10, "rain": 0.0},
        {"desc": "sunny", "tmax": 36, "tmin": 26, "humidity": 55, "wind": 8, "rain": 0.0},
        {"desc": "heavy intensity rain", "tmax": 28, "tmin": 22, "humidity": 92, "wind": 20, "rain": 45.0},
        {"desc": "scattered clouds", "tmax": 33, "tmin": 24, "humidity": 70, "wind": 11, "rain": 0.5}
    ]
    
    for i in range(7):
        day = now + datetime.timedelta(days=i)
        pattern = weather_patterns[i % len(weather_patterns)]
        forecast.append({
            "date": day.strftime("%d %b"),
            "temp_max": pattern["tmax"],
            "temp_min": pattern["tmin"],
            "description": pattern["desc"],
            "humidity": pattern["humidity"],
            "wind_speed": pattern["wind"],
            "rain_mm": pattern["rain"]
        })
        
    return {
        "location": f"{district} (Mock)",
        "forecast": forecast
    }

def get_weather_advice(
    crop: str,
    forecast: dict,
    lang: str,
    settings: dict
) -> str:
    """
    Generates specific farming actions/advice based on a 7-day weather forecast.

    Parameters:
        crop (str): The name of the crop.
        forecast (dict): The weather forecast dictionary structure.
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM provider settings configuration.

    Returns:
        str: Actionable advice string, or an error string starting with "Error:".
    """
    try:
        if "error" in forecast:
            return f"Error: Cannot generate weather advice because weather data contains error: {forecast['error']}"

        # Create a simple weather summary string to feed into the prompt
        location = forecast.get("location", "the region")
        summary_lines = []
        for f in forecast.get("forecast", []):
            line = f"- {f['date']}: Max Temp: {f['temp_max']}°C, Min Temp: {f['temp_min']}°C, {f['description']}, Humidity: {f['humidity']}%, Rain: {f['rain_mm']}mm, Wind: {f['wind_speed']}km/h"
            summary_lines.append(line)
        
        forecast_summary = "\n".join(summary_lines)

        system_instruction = get_language_instruction(lang)
        system_prompt = (
            f"{system_instruction}\n"
            "You are an expert agrometeorologist assistant who guides farmers based on weather forecasts."
        )

        user_prompt = (
            f"Given this 7-day weather forecast for {crop} crop in {location}:\n\n"
            f"{forecast_summary}\n\n"
            f"What specific farming actions should the farmer take this week? "
            f"Provide practical advice regarding irrigation, pesticide spraying, fertilizer application, and harvesting."
        )

        response = get_response(user_prompt, system_prompt, settings)
        return response

    except Exception as e:
        return f"Error: {str(e)}"
